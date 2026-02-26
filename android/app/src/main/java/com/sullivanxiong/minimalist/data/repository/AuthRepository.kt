package com.sullivanxiong.minimalist.data.repository

import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import com.sullivanxiong.minimalist.data.api.MinimalistApi
import com.sullivanxiong.minimalist.data.model.LoginRequest
import com.sullivanxiong.minimalist.data.model.RefreshRequest
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AuthRepository @Inject constructor(
    private val api: MinimalistApi,
    private val dataStore: DataStore<Preferences>,
) {
    companion object {
        private val ACCESS_TOKEN = stringPreferencesKey("access_token")
        private val REFRESH_TOKEN = stringPreferencesKey("refresh_token")
    }

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
                Result.success(Unit)
            } else {
                Result.failure(Exception("Invalid credentials"))
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
                dataStore.edit {
                    it[ACCESS_TOKEN] = response.body()!!.access
                }
                true
            } else false
        } catch (_: Exception) { false }
    }

    suspend fun logout() {
        dataStore.edit {
            it.remove(ACCESS_TOKEN)
            it.remove(REFRESH_TOKEN)
        }
    }

    suspend fun isLoggedIn(): Boolean = getAccessToken() != null
}
