package com.sullivanxiong.minimalist.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.sullivanxiong.minimalist.ui.auth.AuthCheckState
import com.sullivanxiong.minimalist.ui.auth.LoginScreen
import com.sullivanxiong.minimalist.ui.auth.LoginViewModel
import com.sullivanxiong.minimalist.ui.kanban.KanbanScreen
import com.sullivanxiong.minimalist.ui.theme.BgPrimary

@Composable
fun MinimalistApp() {
    val loginViewModel: LoginViewModel = hiltViewModel()
    val authState by loginViewModel.authState.collectAsState()

    when (authState) {
        is AuthCheckState.Loading -> {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(BgPrimary),
            )
        }
        is AuthCheckState.Authenticated, is AuthCheckState.Unauthenticated -> {
            val navController = rememberNavController()
            val startDestination = if (authState is AuthCheckState.Authenticated) "kanban" else "login"

            NavHost(
                navController = navController,
                startDestination = startDestination,
            ) {
                composable("login") {
                    LoginScreen(
                        onLoginSuccess = {
                            navController.navigate("kanban") {
                                popUpTo("login") { inclusive = true }
                            }
                        },
                    )
                }
                composable("kanban") {
                    KanbanScreen()
                }
            }
        }
    }
}
