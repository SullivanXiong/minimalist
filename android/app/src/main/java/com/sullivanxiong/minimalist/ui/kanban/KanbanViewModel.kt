package com.sullivanxiong.minimalist.ui.kanban

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.sullivanxiong.minimalist.data.api.MinimalistApi
import com.sullivanxiong.minimalist.data.api.WebSocketClient
import com.sullivanxiong.minimalist.data.model.Issue
import com.sullivanxiong.minimalist.data.model.Project
import com.sullivanxiong.minimalist.data.model.Workspace
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class KanbanViewModel @Inject constructor(
    private val api: MinimalistApi,
    private val webSocketClient: WebSocketClient,
) : ViewModel() {

    private val _workspaces = MutableStateFlow<List<Workspace>>(emptyList())
    val workspaces: StateFlow<List<Workspace>> = _workspaces.asStateFlow()

    private val _selectedWorkspace = MutableStateFlow<Workspace?>(null)
    val selectedWorkspace: StateFlow<Workspace?> = _selectedWorkspace.asStateFlow()

    private val _projects = MutableStateFlow<List<Project>>(emptyList())
    val projects: StateFlow<List<Project>> = _projects.asStateFlow()

    private val _selectedProject = MutableStateFlow<Project?>(null)
    val selectedProject: StateFlow<Project?> = _selectedProject.asStateFlow()

    private val _issues = MutableStateFlow<List<Issue>>(emptyList())
    val issues: StateFlow<List<Issue>> = _issues.asStateFlow()

    private val _isLoading = MutableStateFlow(true)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()

    init {
        loadWorkspaces()
    }

    private fun loadWorkspaces() {
        viewModelScope.launch {
            try {
                val response = api.getWorkspaces()
                if (response.isSuccessful) {
                    val workspaces = response.body() ?: emptyList()
                    _workspaces.value = workspaces
                    workspaces.firstOrNull()?.let { selectWorkspace(it) }
                } else {
                    _error.value = "Failed to load workspaces (HTTP ${response.code()})"
                }
            } catch (e: Exception) {
                _error.value = "Failed to load workspaces: ${e.message}"
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun selectWorkspace(workspace: Workspace) {
        _selectedWorkspace.value = workspace
        loadProjects(workspace.slug)
        webSocketClient.connect(workspace.slug)
    }

    private fun loadProjects(workspaceSlug: String) {
        viewModelScope.launch {
            try {
                val response = api.getProjects(workspaceSlug)
                if (response.isSuccessful) {
                    val projects = response.body() ?: emptyList()
                    _projects.value = projects
                    projects.firstOrNull()?.let { selectProject(it) }
                } else {
                    _error.value = "Failed to load projects (HTTP ${response.code()})"
                }
            } catch (e: Exception) {
                _error.value = "Failed to load projects: ${e.message}"
            }
        }
    }

    fun selectProject(project: Project) {
        _selectedProject.value = project
        loadIssues()
    }

    private fun loadIssues() {
        val slug = _selectedWorkspace.value?.slug ?: return
        val projectId = _selectedProject.value?.id
        viewModelScope.launch {
            try {
                val response = api.getIssues(slug, projectId)
                if (response.isSuccessful) {
                    _issues.value = response.body() ?: emptyList()
                } else {
                    _error.value = "Failed to load issues (HTTP ${response.code()})"
                }
            } catch (e: Exception) {
                _error.value = "Failed to load issues: ${e.message}"
            }
        }
    }

    override fun onCleared() {
        super.onCleared()
        webSocketClient.disconnect()
    }
}
