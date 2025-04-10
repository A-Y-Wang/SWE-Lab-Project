import React, { useState } from 'react';
import './css/D_addProjectCard.css';

const D_addProjectCard = (props) => {
    // State for input fields
    const [projectName, setProjectName] = useState('');
    const [projectDescription, setProjectDescription] = useState('');

    // Handlers for input changes
    const handleNameChange = (event) => {
        setProjectName(event.target.value);
    };

    const handleDescriptionChange = (event) => {
        setProjectDescription(event.target.value);
    };

    // Placeholder add functionality
    const handleAddClick = () => {
        console.log('Adding Project:', { projectName, projectDescription });
        if (props.onAddProject) {
          props.onAddProject(projectName, projectDescription);
        }
        
        // Reset fields
        setProjectName('');
        setProjectDescription('');
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
