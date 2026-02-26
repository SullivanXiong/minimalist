package com.sullivanxiong.minimalist.ui

import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.sullivanxiong.minimalist.ui.auth.LoginScreen
import com.sullivanxiong.minimalist.ui.auth.LoginViewModel
import com.sullivanxiong.minimalist.ui.kanban.KanbanScreen

@Composable
fun MinimalistApp() {
    val navController = rememberNavController()
    val loginViewModel: LoginViewModel = hiltViewModel()
    val isLoggedIn by loginViewModel.isLoggedIn.collectAsState(initial = false)

    NavHost(
        navController = navController,
        startDestination = if (isLoggedIn) "kanban" else "login",
    ) {
        composable("login") {
            LoginScreen(
                viewModel = loginViewModel,
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
