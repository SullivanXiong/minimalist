package com.sullivanxiong.minimalist.data.api

import android.util.Log
import com.squareup.moshi.Moshi
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import okhttp3.*
import javax.inject.Inject
import javax.inject.Named
import javax.inject.Singleton

sealed class WsMessage {
    data class WorkspaceState(val data: Map<String, Any?>) : WsMessage()
    data class IssueCreated(val data: Map<String, Any?>) : WsMessage()
    data class IssueUpdated(val data: Map<String, Any?>) : WsMessage()
    data class IssueDeleted(val data: Map<String, Any?>) : WsMessage()
    data class ProjectCreated(val data: Map<String, Any?>) : WsMessage()
    data class ProjectUpdated(val data: Map<String, Any?>) : WsMessage()
    data class ProjectDeleted(val data: Map<String, Any?>) : WsMessage()
    data class Error(val message: String) : WsMessage()
    data class Unknown(val type: String, val data: Any?) : WsMessage()
}

private const val TAG = "WebSocketClient"

@Singleton
class WebSocketClient @Inject constructor(
    private val okHttpClient: OkHttpClient,
    private val moshi: Moshi,
    @Named("baseUrl") private val baseUrl: String,
) {
    private var webSocket: WebSocket? = null
    private val _messages = MutableSharedFlow<WsMessage>(replay = 0, extraBufferCapacity = 64)
    val messages: Flow<WsMessage> = _messages.asSharedFlow()

    /**
     * Connect to a workspace WebSocket using only the slug. Uses the injected
     * base URL. For authenticated connections use connect(baseUrl, slug, token).
     */
    fun connect(workspaceSlug: String) {
        connect(baseUrl, workspaceSlug, token = null)
    }

    fun connect(baseUrl: String, workspaceSlug: String, token: String?) {
        // Cancel any existing connection before opening a new one
        webSocket?.cancel()
        webSocket = null

        val wsUrl = baseUrl
            .replace("https://", "wss://")
            .replace("http://", "ws://")
        var url = "$wsUrl/ws/workspace/$workspaceSlug/"
        if (token != null) {
            url = "$url?token=$token"
        }

        val request = Request.Builder().url(url).build()
        webSocket = okHttpClient.newWebSocket(request, object : WebSocketListener() {
            override fun onMessage(webSocket: WebSocket, text: String) {
                val msg = parseMessage(text)
                _messages.tryEmit(msg)
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                Log.e(TAG, "WebSocket failure: ${t.message}", t)
                _messages.tryEmit(WsMessage.Error(t.message ?: "Unknown WebSocket error"))
            }
        })
    }

    fun send(type: String, data: Map<String, Any?>): Boolean {
        val ws = webSocket ?: return false
        return try {
            val message = mapOf("type" to type, "data" to data)
            @Suppress("UNCHECKED_CAST")
            val json = moshi.adapter(Map::class.java as Class<Map<String, Any?>>).toJson(message)
            ws.send(json)
        } catch (e: Exception) {
            Log.e(TAG, "Failed to send message of type '$type': ${e.message}", e)
            false
        }
    }

    fun disconnect() {
        webSocket?.close(1000, "Closing")
        webSocket = null
    }

    @Suppress("UNCHECKED_CAST")
    private fun parseMessage(text: String): WsMessage {
        return try {
            val map = moshi.adapter(Map::class.java).fromJson(text) as? Map<String, Any?>
                ?: return WsMessage.Error("Failed to parse WebSocket message: null result")
            val type = map["type"] as? String ?: ""
            val data = (map["data"] as? Map<String, Any?>) ?: emptyMap()
            when (type) {
                "workspace_state" -> WsMessage.WorkspaceState(data)
                "issue_created" -> WsMessage.IssueCreated(data)
                "issue_updated" -> WsMessage.IssueUpdated(data)
                "issue_deleted" -> WsMessage.IssueDeleted(data)
                "project_created" -> WsMessage.ProjectCreated(data)
                "project_updated" -> WsMessage.ProjectUpdated(data)
                "project_deleted" -> WsMessage.ProjectDeleted(data)
                "error" -> WsMessage.Error(map["message"] as? String ?: "Unknown server error")
                else -> WsMessage.Unknown(type, map["data"])
            }
        } catch (e: Exception) {
            Log.d(TAG, "Failed to parse WebSocket message: ${e.message}. Raw: $text")
            WsMessage.Error("Parse error: ${e.message}")
        }
    }
}
