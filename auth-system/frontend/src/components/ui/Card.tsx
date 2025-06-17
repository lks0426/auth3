import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  // Add any custom props here, e.g., title, footer
}

const Card: React.FC<CardProps> = ({ children, ...props }) => {
  return <div {...props}>{children}</div>;
};

export default Card;
