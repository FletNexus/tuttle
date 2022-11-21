from typing import Mapping

from authentication.auth_data_keys import USER_ID
from core.abstractions import LocalCache
from projects.abstractions import ProjectIntentsResult, ProjectsIntent
from projects.projects_data_source_impl import ProjectDataSourceImpl
from projects.projects_model import Project


class ProjectIntentImpl(ProjectsIntent):
    def __init__(self, cache: LocalCache):
        super().__init__(cache=cache, dataSource=ProjectDataSourceImpl())
        self.allProjectsCache: Mapping[str, Project] = None
        self.completedProjectsCache: Mapping[str, Project] = None
        self.activeProjectsCache: Mapping[str, Project] = None
        self.upcomingProjectsCache: Mapping[str, Project] = None

    def get_total_projects_count(self) -> int:
        result = self.dataSource.get_total_projects_count()
        if result.wasIntentSuccessful:
            return result.data
        else:
            # TODO log error
            return 0

    def get_completed_projects(self):
        if not self.completedProjectsCache:
            self.completedProjectsCache = {}
            for key in self.allProjectsCache:
                p = self.allProjectsCache[key]
                if p.is_completed:
                    self.completedProjectsCache[key] = p
        return self.completedProjectsCache

    def get_active_projects(self):
        if not self.activeProjectsCache:
            self.activeProjectsCache = {}
            for key in self.allProjectsCache:
                p = self.allProjectsCache[key]
                if p.is_active():
                    self.activeProjectsCache[key] = p
        return self.activeProjectsCache

    def get_upcoming_projects(self):
        if not self.upcomingProjectsCache:
            self.upcomingProjectsCache = {}
            for key in self.allProjectsCache:
                p = self.allProjectsCache[key]
                if p.is_upcoming():
                    self.upcomingProjectsCache[key] = p
        return self.upcomingProjectsCache

    def _clear_cached_results(self):
        self.allProjectsCache = None
        self.completedProjectsCache = None
        self.activeProjectsCache = None
        self.upcomingProjectsCache = None

    def get_all_projects(self) -> Mapping[str, Project]:
        if self.activeProjectsCache:
            # return cached results
            return self.activeProjectsCache

        # fetch from data source
        self._clear_cached_results()
        result = self.dataSource.get_all_projects_as_map()
        if result.wasIntentSuccessful:
            self.allProjectsCache = result.data
            return self.allProjectsCache
        else:
            # TODO log error
            return {}

    def cache_projects_data(self, key: str, data: any):
        self.cache.set_value(key, data)