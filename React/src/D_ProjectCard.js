import React, { useState, useEffect } from 'react';
import './css/D_ProjectCard.css';

const D_ProjectCard = ({ project = null }) => {
  // Use provided project data or fallback to default values
  const initialProjectData = project || {
    project_name: "Project Title",
    project_id: "12345",
    description: "Project Description",
    users: ["User1", "User2", "User3"],
    items: [
      { item_name: "Hardware 1", quantity: 5 },
      { item_name: "Hardware 2", quantity: 3 },
    ],
  };

  // Create a mutable copy of the project data
  const [projectData, setProjectData] = useState(initialProjectData);
  
  // State for dropdown selections
  const [selectedItem, setSelectedItem] = useState('');
  const [selectedQuantity, setSelectedQuantity] = useState(0);
  const [selectedUser, setSelectedUser] = useState('');
  
  // State for button label ("JOIN" or "LEAVE")
  const [isJoined, setIsJoined] = useState(false);
  
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

  // Toggle join/leave and add/remove placeholder user
  const toggleJoinLeave = () => {
    if (isJoined) {
      // Remove placeholder user
      const updatedUsers = projectData.users.filter(user => user !== placeholderUser);
      setProjectData({
        ...projectData,
        users: updatedUsers
      });
    } else {
      // Add placeholder user
      const updatedUsers = [...projectData.users, placeholderUser];
      setProjectData({
        ...projectData,
        users: updatedUsers
      });
    }
    setIsJoined(!isJoined);
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

      <div className="attribute item-quantity">
        Number of Items: {selectedQuantity}
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

      <div className="join-button-container">
        <button className="attribute join-button" onClick={toggleJoinLeave}>
          {isJoined ? 'LEAVE' : 'JOIN'}
        </button>
      </div>
    </div>
  );
};

export default D_ProjectCard;
