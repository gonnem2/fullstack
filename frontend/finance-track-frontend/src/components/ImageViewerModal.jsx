    import React from 'react';

    export default function ImageViewerModal({ isOpen, onClose, imageUrl, title }) {
      if (!isOpen) return null
      console.log("ImageViewerModal imageUrl:", imageUrl);
      return (
        <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50" onClick={onClose}>
          <div className="relative max-w-3xl max-h-full p-4" onClick={(e) => e.stopPropagation()}>
            <img src={imageUrl} alt={title} className="max-w-full max-h-screen object-contain rounded-lg shadow-2xl" />
            <button
              onClick={onClose}
              className="absolute top-4 right-4 text-white bg-black/50 rounded-full p-2 hover:bg-black/70"
            >
              ✕
            </button>
          </div>
        </div>
      );
    }