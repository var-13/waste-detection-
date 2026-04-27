import React, { useState } from 'react';
import Modal from './Modal';
import './ImageUploadModal.css';

export default function ImageUploadModal() {
  const [isOpen, setIsOpen] = useState(false);
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setImage(e.target.files[0] || null);
  };

  const handleUpload = async () => {
    if (!image) return;
    setLoading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', image);
      
      const response = await fetch('/api/detect', {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      console.log('Result:', data);
      setIsOpen(false);
      setImage(null);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button className="upload-btn" onClick={() => setIsOpen(true)}>
        Upload Image
      </button>

      <Modal 
        isOpen={isOpen} 
        onClose={() => { setIsOpen(false); setImage(null); }}
        title="Detect Waste"
      >
        <div className="modal-body">
          <label className="file-input">
            <input type="file" accept="image/*" onChange={handleFileChange} />
            <span>{image ? image.name : 'Choose Image'}</span>
          </label>

          <div className="modal-actions">
            <button className="btn-cancel" onClick={() => setIsOpen(false)}>
              Cancel
            </button>
            <button 
              className="btn-detect"
              onClick={handleUpload}
              disabled={!image || loading}
            >
              {loading ? 'Uploading...' : 'Detect'}
            </button>
          </div>
        </div>
      </Modal>
    </>
  );
}
