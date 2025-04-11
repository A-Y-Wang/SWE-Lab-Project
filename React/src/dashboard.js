import React, { useState, useEffect } from 'react';
import D_ProjectCard from './D_ProjectCard';
import D_addProjectCard from './D_addProjectCard';
import './css/dashboard.css';

const Dashboard = () => {
    const [user, setUser] = useState(null);
    
    // Retrieve user data from localStorage
    useEffect(() => {
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        setUser(JSON.parse(storedUser));
      }
    }, []);
  
    // Function to fetch all projects
    const getProjects = async () => {
      try {
        const response = await fetch('/api/projects');
        
        if (!response.ok) {
          throw new Error(`Error: ${response.status}`);
        }
        
        return await response.json();
      } catch (err) {
        console.print("Failed to fetch projects:", err);
        // Return default projects if API call fails
        return [
          { project_name: "Project 1", project_id: "001", description: "Description for Project Alpha", users: ["Alice", "Bob", "Charlie"], items: [ { item_name: "Hardware A", quantity: 10 }, { item_name: "Hardware B", quantity: 7 }, ] },
          { project_name: "Project 2", project_id: "002", description: "Description for Project Beta", users: ["David", "Eve", "Frank"], items: [ { item_name: "Hardware C", quantity: 4 }, { item_name: "Hardware D", quantity: 6 }, ] },
          { project_name: "Project 3", project_id: "003", description: "Description for Project Gamma", users: ["Grace", "Heidi", "Ivan"], items: [ { item_name: "Hardware E", quantity: 8 }, { item_name: "Hardware F", quantity: 2 }, ] },
        ];
      }
    };
  
    // Initialize projects state
    const [projects, setProjects] = useState([]);
  
    // Fetch projects when component mounts
    useEffect(() => {
      const fetchData = async () => {
        const projectData = await getProjects();
        setProjects(projectData);
      };
      
      fetchData();
    }, []);

  // State for search query
  const [searchQuery, setSearchQuery] = useState('');
  // State for error message
  const [errorMessage, setErrorMessage] = useState('');

  // Function to filter projects based on search query
  const filteredProjects = projects.filter(
    (project) => project.project_id === searchQuery
  );

  // Function to handle adding a new project
  const handleAddProject = (projectName, projectDescription, projectID) => {
    // Check if a project with the same project_id already exists
    const isDuplicate = projects.some(
      (project) => project.project_id.toLowerCase() === projectID.toLowerCase()
    );

    if (isDuplicate) {
      // Display error message if duplicate found
      setErrorMessage(`Error: A project with ID "${projectID}" already exists.`);
    } else {
      // Add the new project if no duplicate is found
      const newProject = {
        project_name: projectName,
        project_id: projectID,
        description: projectDescription,
        users: [],
        items: [],
      };
      setProjects([...projects, newProject]);
      setErrorMessage(''); // Clear any previous error messages
    }
  };

  return (
    <div className="dashboard-container">
      <div className="search-container">
        <input
          type="text"
          placeholder="Search Project ID"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-input"
        />
      </div>

      {/* Display error message if it exists */}
      {errorMessage && <p className="error-message">{errorMessage}</p>}

      <div className="projects-container">
        {/* Render only filtered projects */}
        {filteredProjects.map((project) => (
          <D_ProjectCard key={project.project_id} project={project} />
        ))}
      </div>

      <div className="add-project-container">
        <D_addProjectCard onAddProject={handleAddProject} />
      </div>
    </div>
  );
};

export default Dashboard;
