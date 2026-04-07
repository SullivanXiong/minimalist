package com.sullivanxiong.minimalist.data.repository

import android.util.Base64
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import com.sullivanxiong.minimalist.data.api.MinimalistApi
import com.sullivanxiong.minimalist.data.model.LoginRequest
import com.sullivanxiong.minimalist.data.model.RefreshRequest
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.launch
import org.json.JSONObject
import javax.inject.Inject
import javax.inject.Singleton

// TODO: For production hardening, migrate token storage to EncryptedSharedPreferences
//       (androidx.security:security-crypto) to encrypt tokens at rest on the device.
//       DataStore with backup exclusion rules (backup_rules.xml) is the current approach.

@Singleton
class AuthRepository @Inject constructor(
    private val api: MinimalistApi,
    private val dataStore: DataStore<Preferences>,
) {
    companion object {
        private val ACCESS_TOKEN = stringPreferencesKey("access_token")
        private val REFRESH_TOKEN = stringPreferencesKey("refresh_token")
    }

    @Volatile
    private var cachedAccessToken: String? = null

    init {
        // Pre-populate the in-memory cache from DataStore so the interceptor never
        // needs to block on a coroutine for the common (non-401) path.
        CoroutineScope(Dispatchers.IO + SupervisorJob()).launch {
            cachedAccessToken = dataStore.data.map { it[ACCESS_TOKEN] }.first()
        }
    }

    /** Synchronous read for use by AuthInterceptor on the OkHttp thread pool. */
    fun getAccessTokenSync(): String? = cachedAccessToken

    suspend fun getAccessToken(): String? =
        dataStore.data.map { it[ACCESS_TOKEN] }.first()

    suspend fun login(username: String, password: String): Result<Unit> {
        return try {
            val response = api.login(LoginRequest(username, password))
            if (response.isSuccessful && response.body() != null) {
                val tokens = response.body()!!
                dataStore.edit {
                    it[ACCESS_TOKEN] = tokens.access
                    it[REFRESH_TOKEN] = tokens.refresh
                }
                cachedAccessToken = tokens.access
                Result.success(Unit)
            } else {
                val errorMessage = try {
                    response.errorBody()?.string()
                        ?.let { body -> JSONObject(body).optString("detail", "") }
                    ?.ifEmpty { null }
                        ?: "Login failed (HTTP ${response.code()})"
                } catch (_: Exception) {
                    "Login failed (HTTP ${response.code()})"
                }
                Result.failure(Exception(errorMessage))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun refreshToken(): Boolean {
        val refresh = dataStore.data.map { it[REFRESH_TOKEN] }.first() ?: return false
        return try {
            val response = api.refresh(RefreshRequest(refresh))
            if (response.isSuccessful && response.body() != null) {
                val tokens = response.body()!!
                // Persist both tokens — server has ROTATE_REFRESH_TOKENS=True, so the old
                // refresh token becomes invalid immediately after this call.
                dataStore.edit {
                    it[ACCESS_TOKEN] = tokens.access
                    it[REFRESH_TOKEN] = tokens.refresh
                }
                cachedAccessToken = tokens.access
                true
            } else false
        } catch (_: Exception) { false }
    }

    suspend fun logout() {
        cachedAccessToken = null
        dataStore.edit {
            it.remove(ACCESS_TOKEN)
            it.remove(REFRESH_TOKEN)
        }
    }

    suspend fun isLoggedIn(): Boolean {
        val accessToken = getAccessToken()
        val refreshToken = dataStore.data.map { it[REFRESH_TOKEN] }.first()

        if (accessToken == null && refreshToken == null) return false

        // If we have a refresh token, we consider the user logged in regardless of whether
        // the access token is expired. The interceptor handles token refresh on the next API call.
        if (refreshToken != null) return true

        // No refresh token — fall back to checking whether the access token is still valid.
        return accessToken != null && !isJwtExpired(accessToken)
    }

    /**
     * Decodes the JWT payload (middle segment) and checks the `exp` claim.
     * Returns true if the token is expired or unparseable (fail-safe: treat unknown as expired).
     */
    private fun isJwtExpired(token: String): Boolean {
        return try {
            val parts = token.split(".")
            if (parts.size != 3) return true
            // JWT uses base64url encoding without padding
            val payload = Base64.decode(parts[1], Base64.URL_SAFE or Base64.NO_PADDING or Base64.NO_WRAP)
            val json = JSONObject(String(payload, Charsets.UTF_8))
            val exp = json.optLong("exp", -1L)
            if (exp == -1L) return true
            val nowSeconds = System.currentTimeMillis() / 1000L
            nowSeconds >= exp
        } catch (_: Exception) {
            true
        }
    }
}
