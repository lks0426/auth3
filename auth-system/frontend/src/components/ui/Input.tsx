import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  // Add any custom props here, e.g., label
}

const Input: React.FC<InputProps> = (props) => {
  return <input {...props} />;
};

export default Input;
