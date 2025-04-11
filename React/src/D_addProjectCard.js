import React, { useState } from 'react';
import './css/D_addProjectCard.css';

//Need to import user from backend  const userId = user ? user.UserId : null;

const D_addProjectCard = (props) => {
    // State for input fields
    const [projectName, setProjectName] = useState('');
    const [projectDescription, setProjectDescription] = useState('');
    const [projectID, setProjectID] = useState('');

    // Handlers for input changes
    const handleNameChange = (event) => {
        setProjectName(event.target.value);
    };

    const handleDescriptionChange = (event) => {
        setProjectDescription(event.target.value);
    };

    const handleIDChange = (event) => {
        setProjectID(event.target.value);
    }

    // Placeholder add functionality 
    const handleAddClick = () => {
        console.log('Adding Project:', { projectName, projectDescription, projectID });
        if (props.onAddProject) {
          props.onAddProject(projectName, projectDescription, projectID);
        }
        
        // Reset fields
        setProjectName('');
        setProjectDescription('');
        setProjectID('');
    };

    return (
        <div className="add-project-card-horizontal">
            {/* Input for Project Name */}
            <div className="attribute-input">
                <input
                    type="text"
                    placeholder="Enter Title"
                    value={projectName}
                    onChange={handleNameChange}
                />
            </div>

            {/* Input for Project Description */}
            <div className="attribute-input">
                <input
                    type="text"
                    placeholder="Enter Project Description"
                    value={projectDescription}
                    onChange={handleDescriptionChange}
                />
            </div>

            {/* Input for Project ID */}
            <div className="attribute-input">
                <input
                    type="text"
                    placeholder="Enter Project ID"
                    value={projectID}
                    onChange={handleIDChange}
                />
            </div>

            {/* Add Button */}
            <div className="add-button-container">
                <button className="attribute-input" onClick={handleAddClick}>
                    Add
                </button>
            </div>
        </div>
    );
};

export default D_addProjectCard;
