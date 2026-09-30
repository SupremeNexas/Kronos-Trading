import React, { useState, useEffect } from 'react';

interface FadeInProps {
  delay?: number; // Delay in milliseconds
  duration?: number; // Tailwind transition duration override (default is 1000)
  className?: string;
  children: React.ReactNode;
}

export const FadeIn: React.FC<FadeInProps> = ({
  delay = 0,
  duration = 1000,
  className = "",
  children
}) => {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(true);
    }, delay);
    return () => clearTimeout(timer);
  }, [delay]);

  return (
    <div
      className={`transition-opacity ease-out ${className}`}
      style={{
        transitionDuration: `${duration}ms`,
        opacity: visible ? 1 : 0
      }}
    >
      {children}
    </div>
  );
};
