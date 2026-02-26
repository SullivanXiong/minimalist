package com.sullivanxiong.minimalist.data.api

import com.sullivanxiong.minimalist.data.model.*
import retrofit2.Response
import retrofit2.http.*

interface MinimalistApi {

    // Auth
    @POST("api/auth/login/")
    suspend fun login(@Body request: LoginRequest): Response<AuthTokens>

    @POST("api/auth/refresh/")
    suspend fun refresh(@Body request: RefreshRequest): Response<AuthTokens>

    // Workspaces
    @GET("api/v1/workspaces/")
    suspend fun getWorkspaces(): Response<List<Workspace>>

    @GET("api/v1/workspaces/{slug}/")
    suspend fun getWorkspace(@Path("slug") slug: String): Response<Workspace>

    // Projects
    @GET("api/v1/workspaces/{slug}/projects/")
    suspend fun getProjects(@Path("slug") workspaceSlug: String): Response<List<Project>>

    // Issues
    @GET("api/v1/workspaces/{slug}/issues/")
    suspend fun getIssues(
        @Path("slug") workspaceSlug: String,
        @Query("project_id") projectId: String? = null,
    ): Response<List<Issue>>

    @POST("api/v1/workspaces/{slug}/issues/")
    suspend fun createIssue(
        @Path("slug") workspaceSlug: String,
        @Body request: IssueCreateRequest,
    ): Response<Issue>

    @PATCH("api/v1/workspaces/{slug}/issues/{id}/")
    suspend fun updateIssue(
        @Path("slug") workspaceSlug: String,
        @Path("id") issueId: String,
        @Body updates: Map<String, @JvmSuppressWildcards Any>,
    ): Response<Issue>

    @POST("api/v1/workspaces/{slug}/issues/{id}/move/")
    suspend fun moveIssue(
        @Path("slug") workspaceSlug: String,
        @Path("id") issueId: String,
        @Body body: Map<String, String>,
    ): Response<Issue>

    // Labels
    @GET("api/v1/workspaces/{slug}/labels/")
    suspend fun getLabels(@Path("slug") workspaceSlug: String): Response<List<Label>>
}
