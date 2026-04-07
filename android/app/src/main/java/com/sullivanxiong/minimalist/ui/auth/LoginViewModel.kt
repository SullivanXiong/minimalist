package com.sullivanxiong.minimalist.ui.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.sullivanxiong.minimalist.data.repository.AuthRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed interface AuthCheckState {
    data object Loading : AuthCheckState
    data object Authenticated : AuthCheckState
    data object Unauthenticated : AuthCheckState
}

@HiltViewModel
class LoginViewModel @Inject constructor(
    private val authRepository: AuthRepository,
) : ViewModel() {

    private val _authState = MutableStateFlow<AuthCheckState>(AuthCheckState.Loading)
    val authState: StateFlow<AuthCheckState> = _authState.asStateFlow()

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    init {
        viewModelScope.launch {
            val loggedIn = authRepository.isLoggedIn()
            _authState.value = if (loggedIn) AuthCheckState.Authenticated else AuthCheckState.Unauthenticated
        }
    }

    fun login(username: String, password: String) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            val result = authRepository.login(username, password)
            _isLoading.value = false
            result.fold(
                onSuccess = { _authState.value = AuthCheckState.Authenticated },
                onFailure = { _error.value = it.message },
            )
        }
    }
}
