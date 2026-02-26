package com.sullivanxiong.minimalist.data.api

import com.squareup.moshi.Moshi
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.receiveAsFlow
import okhttp3.*
import javax.inject.Inject
import javax.inject.Singleton

data class WsMessage(
    val type: String,
    val data: Map<String, Any?>,
    val requestId: String? = null,
)

@Singleton
class WebSocketClient @Inject constructor(
    private val okHttpClient: OkHttpClient,
    private val moshi: Moshi,
) {
    private var webSocket: WebSocket? = null
    private val _messages = Channel<WsMessage>(Channel.BUFFERED)
    val messages: Flow<WsMessage> = _messages.receiveAsFlow()

    fun connect(baseUrl: String, workspaceSlug: String, token: String?) {
        disconnect()

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
                try {
                    @Suppress("UNCHECKED_CAST")
                    val map = moshi.adapter(Map::class.java).fromJson(text) as? Map<String, Any?>
                    if (map != null) {
                        val msg = WsMessage(
                            type = map["type"] as? String ?: "",
                            data = (map["data"] as? Map<String, Any?>) ?: emptyMap(),
                            requestId = map["request_id"] as? String,
                        )
                        _messages.trySend(msg)
                    }
                } catch (_: Exception) {}
            }
        })
    }

    fun send(type: String, data: Map<String, Any?>) {
        val message = mapOf("type" to type, "data" to data)
        val json = moshi.adapter(Map::class.java).toJson(message)
        webSocket?.send(json)
    }

    fun disconnect() {
        webSocket?.close(1000, "Closing")
        webSocket = null
    }
}
