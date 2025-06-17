import React from 'react';
import Header from './Header';
import Footer from './Footer';
// import Sidebar from './Sidebar'; // Optional: if you want a sidebar

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="layout">
      <Header />
      {/* <Sidebar /> */}
      <main>{children}</main>
      <Footer />
    </div>
  );
};

export default Layout;
