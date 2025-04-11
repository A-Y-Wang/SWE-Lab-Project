import React, { useState, useEffect } from 'react';
import './css/D_ProjectCard.css';

const D_ProjectCard = ({ project = null }) => {
  // Use provided project data or fallback to default values

  const [user, setUser] = useState(null);
  const userId = user ? user.UserId : null;
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  // const initialProjectData = project || {
  //   project_name: "Project Title",
  //   project_id: "12345",
  //   description: "Project Description",
  //   users: ["User1", "User2", "User3"],
  //   items: [
  //     { item_name: "Hardware 1", quantity: 5 },
  //     { item_name: "Hardware 2", quantity: 3 },
  //   ],
  // };

  // Create a mutable copy of the project data
  const [projectData, setProjectData] = useState(project); //all projects
  const [myProjects, setMyProjects] = useState([]); //my projects
  const [joinInput, setJoinInput] = useState('');
  
  // State for dropdown selections
  const [selectedItem, setSelectedItem] = useState('');
  const [selectedQuantity, setSelectedQuantity] = useState(0);
  const [selectedUser, setSelectedUser] = useState('');
  
  // State for button label ("JOin" or "Leave")

  useEffect(() => {
    setProjectData(project);
  }, [project]);

  const fetchMyProjects = () =>{
    if(!userId) return;
    fetch(`http://localhost:5000/api/user/${userId}/myprojects`)
      .then((res)=> res.json())
      .then((data) => {
        console.log("Fetched my projects:", data);
        setMyProjects(data);
      })
      .catch((error) => console.error("Error fetching my projects:", error));
  }
  useEffect(() => {
    fetchMyProjects();
  }, [userId]);

  const [isJoined, setIsJoined] = useState(false);
  useEffect(() => {
    if (myProjects && projectData.project_id) {
      setIsJoined(myProjects.includes(projectData.project_id));
    }
  }, [myProjects, projectData.project_id]);
  
  // Placeholder user name - this would typically come from the logged-in user
  const placeholderUser = "Current User";

  // Initialize dropdown selections when component mounts or project changes
  useEffect(() => {
    if (projectData.items && projectData.items.length > 0) {
      setSelectedItem(projectData.items[0].item_name);
      setSelectedQuantity(projectData.items[0].quantity);
    }
    
    if (projectData.users && projectData.users.length > 0) {
      setSelectedUser(projectData.users[0]);
    }
  }, [projectData]);

  // Handle item selection change
  const handleItemChange = (event) => {
    const selected = projectData.items.find(item => item.item_name === event.target.value);
    if (selected) {
      setSelectedItem(selected.item_name);
      setSelectedQuantity(selected.quantity);
    }
  };

  // Handle user selection change
  const handleUserChange = (event) => {
    setSelectedUser(event.target.value);
  };

  const [errorMessage, setErrorMessage] = useState('');
  // Toggle join/leave and add/remove placeholder user
  const toggleJoinLeave = async () => {
    // If the user is not yet joined, validate the join input
    if (!isJoined) {
      if (joinInput.trim() !== projectData.project_id) {
        setErrorMessage("Entered Project ID does not match this project.");
        return; // Exit early if the input does not match
      }
  
      // Call the backend API to join the project
      try {
        const response = await fetch('http://localhost:5000/api/user/joinProject', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ userId, projectId: projectData.project_id }),
        });
        const data = await response.json();
        if (!response.ok) {
          setErrorMessage(data.error || "Failed to join project.");
          return;
        }
        // If API call is successful, update the project data state by adding the placeholder user
        setProjectData((prevData) => ({
          ...prevData,
          users: [...prevData.users, placeholderUser],
        }));
        setIsJoined(true);
        setErrorMessage('');
      } catch (error) {
        console.error('Error joining project:', error);
        setErrorMessage('Error joining project');
      }
    } else {
      // If the user is already joined, call the backend API to leave the project
      try {
        const response = await fetch('http://localhost:5000/api/user/leaveProject', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ userId, projectId: projectData.project_id }),
        });
        const data = await response.json();
        if (!response.ok) {
          setErrorMessage(data.error || "Failed to leave project.");
          return;
        }
        // Update the project data state by removing the placeholder user
        setProjectData((prevData) => ({
          ...prevData,
          users: prevData.users.filter((u) => u !== placeholderUser),
        }));
        setIsJoined(false);
        setErrorMessage('');
      } catch (error) {
        console.error('Error leaving project:', error);
        setErrorMessage('Error leaving project');
      }
    }
  };

  return (
    <div className="project-card-horizontal">
      <div className="attribute project-name">
        {projectData.project_name}
      </div>

      <div className="attribute project-description">
        {projectData.description}
      </div>

      <div className="attribute items-dropdown">
        <label>Items: </label>
        <select value={selectedItem} onChange={handleItemChange}>
          {projectData.items.map((item, index) => (
            <option key={index} value={item.item_name}>
              {item.item_name}
            </option>
          ))}
        </select>
      </div>

      <div className="attribute users-dropdown">
        <label>User's: </label>
        <select value={selectedUser} onChange={handleUserChange}>
          {projectData.users.map((user, index) => (
            <option key={index} value={user}>
              {user}
            </option>
          ))}
        </select>
      </div>

      <div className="join-input-container">
        <label htmlFor="joinInput">Enter Project ID:</label>
        <input
          id="joinInput"
          type="text"
          value={joinInput}
          onChange={(e) => setJoinInput(e.target.value)}
          placeholder="Enter project id"
        />
      </div>

      <div className="join-button-container">
        <button className="attribute join-button" onClick={toggleJoinLeave}>
          {isJoined ? 'LEAVE' : 'JOIN'}
        </button>
      </div>
    </div>
  );
};

export default D_ProjectCard;
