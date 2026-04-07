package com.sullivanxiong.minimalist.data.api

import com.sullivanxiong.minimalist.data.repository.AuthRepository
import kotlinx.coroutines.runBlocking
import okhttp3.Interceptor
import okhttp3.Response
import javax.inject.Inject

class AuthInterceptor @Inject constructor(
    private val authRepository: dagger.Lazy<AuthRepository>,
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val token = authRepository.get().getAccessTokenSync()
        val request = if (token != null) {
            chain.request().newBuilder()
                .header("Authorization", "Bearer $token")
                .build()
        } else {
            chain.request()
        }

        val response = chain.proceed(request)

        if (response.code == 401) {
            response.close()
            val refreshed = runBlocking { authRepository.get().refreshToken() }
            if (refreshed) {
                val newToken = authRepository.get().getAccessTokenSync()
                val retryRequest = if (newToken != null) {
                    chain.request().newBuilder()
                        .header("Authorization", "Bearer $newToken")
                        .build()
                } else {
                    chain.request()
                }
                return chain.proceed(retryRequest)
            }
        }

        return response
    }
}
