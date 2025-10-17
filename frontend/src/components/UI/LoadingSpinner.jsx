import React from 'react';

const LoadingSpinner = ({ size = 'large', message = 'Loading...' }) => {
  const sizeClasses = {
    small: 'w-6 h-6',
    medium: 'w-12 h-12',
    large: 'w-16 h-16'
  };

  return (
    <div className="flex flex-col justify-center items-center py-12">
      <div className={`animate-spin rounded-full border-b-2 border-amber-600 ${sizeClasses[size]} mb-4`}></div>
      {message && <p className="text-gray-600 text-center">{message}</p>}
    </div>
  );
};

export default LoadingSpinner;