import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
// Placeholder imports for pages we are about to create
import ProjectsPage from './pages/ProjectsPage';
import ProjectWorkspace from './pages/ProjectWorkspace';
import IdeasPage from './pages/IdeasPage';
import IdeaDetail from './pages/IdeaDetail';
import ResearchPage from './pages/ResearchPage';
import TasksPage from './pages/TasksPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/projects" replace />} />

          <Route path="projects" element={<ProjectsPage />} />
          <Route path="projects/:id" element={<ProjectWorkspace />} />

          <Route path="ideas" element={<IdeasPage />} />
          <Route path="ideas/:id" element={<IdeaDetail />} />

          <Route path="tasks" element={<TasksPage />} />

          <Route path="research" element={<ResearchPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
