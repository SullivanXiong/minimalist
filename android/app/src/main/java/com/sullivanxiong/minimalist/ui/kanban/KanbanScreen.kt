package com.sullivanxiong.minimalist.ui.kanban

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.sullivanxiong.minimalist.data.model.Issue
import com.sullivanxiong.minimalist.data.model.Status
import com.sullivanxiong.minimalist.ui.theme.BgPrimary

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun KanbanScreen() {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Minimalist") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = BgPrimary,
                ),
            )
        },
        containerColor = BgPrimary,
    ) { padding ->
        // Placeholder — will be connected to ViewModel
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            Text(
                "Kanban board will be implemented here",
                color = MaterialTheme.colorScheme.onBackground,
                modifier = Modifier.padding(16.dp),
            )
        }
    }
}

@Composable
fun KanbanColumn(
    status: Status,
    issues: List<Issue>,
    modifier: Modifier = Modifier,
) {
    Card(
        modifier = modifier
            .width(280.dp)
            .fillMaxHeight()
            .padding(4.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color(0xFF141414),
        ),
    ) {
        Column(modifier = Modifier.padding(8.dp)) {
            Text(
                text = status.name,
                style = MaterialTheme.typography.titleSmall,
                color = Color(0xFF8A8A8A),
            )
            Spacer(Modifier.height(8.dp))
            issues.forEach { issue ->
                IssueCard(issue = issue)
                Spacer(Modifier.height(4.dp))
            }
        }
    }
}

@Composable
fun IssueCard(issue: Issue) {
    Card(
        colors = CardDefaults.cardColors(
            containerColor = Color(0xFF1A1A1A),
        ),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Text(
                text = issue.identifier,
                style = MaterialTheme.typography.labelSmall,
                color = Color(0xFF5C5C5C),
            )
            Text(
                text = issue.title,
                style = MaterialTheme.typography.bodyMedium,
                color = Color(0xFFEBEBEB),
            )
        }
    }
}
