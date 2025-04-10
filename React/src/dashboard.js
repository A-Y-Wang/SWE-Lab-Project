import React, { useState } from 'react';
import D_ProjectCard from './D_ProjectCard';
import D_addProjectCard from './D_addProjectCard';
import './css/dashboard.css';

const Dashboard = () => {
  const [projects, setProjects] = useState([
    {
      project_name: "Project 1",
      project_id: "001",
      description: "Description for Project Alpha",
      users: ["Alice", "Bob", "Charlie"],
      items: [
        { item_name: "Hardware A", quantity: 10 },
        { item_name: "Hardware B", quantity: 7 },
      ],
    },
    {
      project_name: "Project 2",
      project_id: "002",
      description: "Description for Project Beta",
      users: ["David", "Eve", "Frank"],
      items: [
        { item_name: "Hardware C", quantity: 4 },
        { item_name: "Hardware D", quantity: 6 },
      ],
    },
    {
      project_name: "Project 3",
      project_id: "003",
      description: "Description for Project Gamma",
      users: ["Grace", "Heidi", "Ivan"],
      items: [
        { item_name: "Hardware E", quantity: 8 },
        { item_name: "Hardware F", quantity: 2 },
      ],
    },
  ]);
  
  // State for search query
  const [searchQuery, setSearchQuery] = useState('');

  // Function to filter projects based on search query
  const filteredProjects = projects.filter(project =>
    project.project_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Function to handle adding a new project
  const handleAddProject = (projectName, projectDescription) => {
    const newProject = {
      project_name: projectName,
      project_id: `00${projects.length + 1}`,
      description: projectDescription,
      users: [],
      items: [],
    };
    setProjects([...projects, newProject]);
  };

  return (
    <div className="dashboard-container">
      <div className="search-container">
        <input
          type="text"
          placeholder="Search Title"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-input"
        />
      </div>
      
      <div className="projects-container">
        {filteredProjects.map((project, index) => (
            <D_ProjectCard key={index} project={project} />
        ))}
      </div>
      
      <div className="add-project-container">
        <D_addProjectCard onAddProject={handleAddProject} />
      </div>

    </div>
  );
};

export default Dashboard;
