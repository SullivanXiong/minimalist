package com.sullivanxiong.minimalist.ui.kanban

import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.sullivanxiong.minimalist.data.model.Issue
import com.sullivanxiong.minimalist.data.model.Status
import com.sullivanxiong.minimalist.ui.theme.BgPrimary
import com.sullivanxiong.minimalist.ui.theme.BgSecondary
import com.sullivanxiong.minimalist.ui.theme.BgSurface
import com.sullivanxiong.minimalist.ui.theme.TextMuted
import com.sullivanxiong.minimalist.ui.theme.TextPrimary
import com.sullivanxiong.minimalist.ui.theme.TextSecondary

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun KanbanScreen(
    viewModel: KanbanViewModel = hiltViewModel(),
) {
    val isLoading by viewModel.isLoading.collectAsState()
    val error by viewModel.error.collectAsState()
    val issues by viewModel.issues.collectAsState()
    val selectedProject by viewModel.selectedProject.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(selectedProject?.name ?: "Minimalist") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = BgPrimary,
                ),
            )
        },
        containerColor = BgPrimary,
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding),
        ) {
            when {
                isLoading -> {
                    CircularProgressIndicator(
                        modifier = Modifier.align(Alignment.Center),
                        color = MaterialTheme.colorScheme.primary,
                    )
                }
                error != null -> {
                    Text(
                        text = error!!,
                        color = MaterialTheme.colorScheme.error,
                        modifier = Modifier
                            .align(Alignment.Center)
                            .padding(16.dp),
                    )
                }
                issues.isEmpty() -> {
                    Text(
                        text = "No issues yet",
                        color = MaterialTheme.colorScheme.onBackground,
                        modifier = Modifier
                            .align(Alignment.Center)
                            .padding(16.dp),
                    )
                }
                else -> {
                    val statuses = selectedProject?.statuses ?: emptyList()
                    val issuesByStatus = issues.groupBy { it.status_id }

                    Row(
                        modifier = Modifier
                            .fillMaxSize()
                            .horizontalScroll(rememberScrollState())
                            .padding(8.dp),
                    ) {
                        statuses.forEach { status ->
                            KanbanColumn(
                                status = status,
                                issues = issuesByStatus[status.id] ?: emptyList(),
                            )
                        }
                        // Render issues with no matching status in an overflow column
                        val knownStatusIds = statuses.map { it.id }.toSet()
                        val orphanedIssues = issues.filter { it.status_id !in knownStatusIds }
                        if (orphanedIssues.isNotEmpty()) {
                            KanbanColumn(
                                status = Status(
                                    id = "",
                                    project_id = selectedProject?.id ?: "",
                                    name = "Other",
                                    category = "unstarted",
                                ),
                                issues = orphanedIssues,
                            )
                        }
                    }
                }
            }
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
            containerColor = BgSecondary,
        ),
    ) {
        Column(
            modifier = Modifier
                .padding(8.dp)
                .verticalScroll(rememberScrollState()),
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    text = status.name,
                    style = MaterialTheme.typography.titleSmall,
                    color = TextSecondary,
                )
                Spacer(Modifier.width(8.dp))
                Text(
                    text = issues.size.toString(),
                    style = MaterialTheme.typography.labelSmall,
                    color = TextMuted,
                )
            }
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
            containerColor = BgSurface,
        ),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Text(
                text = issue.identifier,
                style = MaterialTheme.typography.labelSmall,
                color = TextMuted,
            )
            Text(
                text = issue.title,
                style = MaterialTheme.typography.bodyMedium,
                color = TextPrimary,
            )
        }
    }
}
