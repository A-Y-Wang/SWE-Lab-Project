// import React, { useState } from 'react';
// import D_ProjectCard from './D_ProjectCard';
// import D_addProjectCard from './D_addProjectCard';
// import './css/dashboard.css';

// const Dashboard = () => {
//   // const [user, setUser] = useState(null);
//   // const userId = user ? user.UserId : null;

//   // Retrieve the user data from localStorage when the component mounts
//   // useEffect(() => {
//   //   const storedUser = localStorage.getItem('user');
//   //   if (storedUser) {
//   //     setUser(JSON.parse(storedUser));
//   //   }
//   // }, []);

//   // const getProjects = () =>{
//   //   if(!userId) return;


//   // }
//   const [projects, setProjects] = useState([
//     {
//       project_name: "Project 1",
//       project_id: "001",
//       description: "Description for Project Alpha",
//       users: ["Alice", "Bob", "Charlie"],
//       items: [
//         { item_name: "Hardware A", quantity: 10 },
//         { item_name: "Hardware B", quantity: 7 },
//       ],
//     },
//     {
//       project_name: "Project 2",
//       project_id: "002",
//       description: "Description for Project Beta",
//       users: ["David", "Eve", "Frank"],
//       items: [
//         { item_name: "Hardware C", quantity: 4 },
//         { item_name: "Hardware D", quantity: 6 },
//       ],
//     },
//     {
//       project_name: "Project 3",
//       project_id: "003",
//       description: "Description for Project Gamma",
//       users: ["Grace", "Heidi", "Ivan"],
//       items: [
//         { item_name: "Hardware E", quantity: 8 },
//         { item_name: "Hardware F", quantity: 2 },
//       ],
//     },
//   ]);

//   // State for search query
//   const [searchQuery, setSearchQuery] = useState('');
//   // State for error message
//   const [errorMessage, setErrorMessage] = useState('');

//   // Function to filter projects based on search query
//   const filteredProjects = projects.filter(
//     (project) => project.project_id === searchQuery
//   );

//   // Function to handle adding a new project
//   const handleAddProject = (projectName, projectDescription, projectID) => {
//     // Check if a project with the same project_id already exists
//     const isDuplicate = projects.some(
//       (project) => project.project_id.toLowerCase() === projectID.toLowerCase()
//     );

//     if (isDuplicate) {
//       // Display error message if duplicate found
//       setErrorMessage(`Error: A project with ID "${projectID}" already exists.`);
//     } else {
//       // Add the new project if no duplicate is found
//       const newProject = {
//         project_name: projectName,
//         project_id: projectID,
//         description: projectDescription,
//         users: [],
//         items: [],
//       };
//       setProjects([...projects, newProject]);
//       setErrorMessage(''); // Clear any previous error messages
//     }
//   };

//   return (
//     <div className="dashboard-container">
//       <div className="search-container">
//         <input
//           type="text"
//           placeholder="Search Project ID"
//           value={searchQuery}
//           onChange={(e) => setSearchQuery(e.target.value)}
//           className="search-input"
//         />
//       </div>

//       {/* Display error message if it exists */}
//       {errorMessage && <p className="error-message">{errorMessage}</p>}

//       <div className="projects-container">
//         {/* Render only filtered projects */}
//         {filteredProjects.map((project) => (
//           <D_ProjectCard key={project.project_id} project={project} />
//         ))}
//       </div>

//       <div className="add-project-container">
//         <D_addProjectCard onAddProject={handleAddProject} />
//       </div>
//     </div>
//   );
// };

// export default Dashboard;
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
  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/projects');
        if (!response.ok) {
          throw new Error('Failed to fetch projects');
        }
        const data = await response.json();
        setProjects(data);
      } catch (error) {
        console.error('Error fetching projects:', error);
      }
    };

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
      const response = await fetch('http://localhost:5000/api/projects', {
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
  };

  return (
    <div className="dashboard">
      <div className="checkout-button-container">
        <button onClick={() => navigate('/checkout')}>
          Go to Checkout
        </button>
      </div>
      <h1>Dashboard</h1>

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