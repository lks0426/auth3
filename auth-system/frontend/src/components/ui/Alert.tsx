import React from 'react';

interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  // Add any custom props here, e.g., type (success, error, warning)
}

const Alert: React.FC<AlertProps> = ({ children, ...props }) => {
  return <div role="alert" {...props}>{children}</div>;
};

export default Alert;
