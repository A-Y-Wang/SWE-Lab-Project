import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import D_ProjectCard from './D_ProjectCard';
import D_addProjectCard from './D_addProjectCard';
import './css/dashboard.css';

const Dashboard = () => {
  const [projects, setProjects] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const navigate = useNavigate();

  // Fetch projects from the backend when the component mounts
  const fetchProjects = async () => {
    try {
      const response = await fetch('/api/projects');
      if (!response.ok) {
        throw new Error('Failed to fetch projects');
      }
      const data = await response.json();
      setProjects(data);
    } catch (error) {
      console.error('Error fetching projects:', error);
    }
  };
  useEffect(() => {
    fetchProjects();
  }, []);

  const filteredProjects = projects.filter(
    (project) => project.project_id === searchQuery
  );

  const handleAddProject = async (projectName, projectDescription, projectID) => {
    //cant have the same project id
    const isDuplicate = projects.some(
      (project) => project.project_id.toLowerCase() === projectID.toLowerCase()
    );
    if (isDuplicate) {
      setErrorMessage(`Error: A project with ID "${projectID}" already exists.`);
      setTimeout(() => {
        console.log("clearing message now");
        setErrorMessage('');
      }, 2000);
      return; // Exit early if duplicate exists
    }  
    const newProject = {
      project_name: projectName,
      project_id: projectID,
      description: projectDescription,
      users: [],
      items: [],
    };
    try {
      const response = await fetch('/api/createprojects', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newProject),
      });
  
      const data = await response.json();
  
      if (response.ok) {
        console.log('Project created:', data);
        setProjects([...projects, newProject]);
        setErrorMessage('');
      } else {
        setErrorMessage(`Error: ${data.error}`);
      }
    } catch (error) {
      console.error('Error creating project:', error);
      setErrorMessage('Error creating project');
    }
    fetchProjects();
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div className="checkout-button-container">
          <button onClick={() => navigate('/checkout')}>
            Go to Checkout
          </button>
        </div>
          <h1>Dashboard</h1>
      </div>

      {/* Search Bar */}
      <input
        type="text"
        placeholder="Search by Project ID..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
      />

      {errorMessage && <div className="error">{errorMessage}</div>}

      {/* Add Project Card */}
      <D_addProjectCard onAddProject={handleAddProject} />

      {/* Render Projects */}
      <div className="project-list">
        {(searchQuery ? filteredProjects : projects).map((project) => (
          <D_ProjectCard key={project.project_id} project={project} />
        ))}
      </div>
    </div>
  );
};

export default Dashboard;