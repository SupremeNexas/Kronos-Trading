import React, { useState, useEffect } from 'react';

interface AnimatedHeadingProps {
  text: string;
}

export const AnimatedHeading: React.FC<AnimatedHeadingProps> = ({ text }) => {
  const [animate, setAnimate] = useState(false);

  useEffect(() => {
    // Start the animation after 200ms initial delay
    const timer = setTimeout(() => {
      setAnimate(true);
    }, 200);
    return () => clearTimeout(timer);
  }, []);

  // Split text by literal \n or actual newline character
  const lines = text.split(/\\n|\n/);
  const charDelay = 30; // 30ms staggered delay

  return (
    <h1
      className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-normal text-white mb-4 leading-tight tracking-tight select-none"
      style={{ letterSpacing: '-0.04em' }}
    >
      {lines.map((line, lineIndex) => {
        const lineLength = line.length;
        return (
          <div key={lineIndex} className="block">
            {line.split('').map((char, charIndex) => {
              // Formula: (lineIndex * lineLength * charDelay) + (charIndex * charDelay)
              const delay = (lineIndex * lineLength * charDelay) + (charIndex * charDelay);

              return (
                <span
                  key={charIndex}
                  className="inline-block transition-all ease-out"
                  style={{
                    transitionDuration: '500ms',
                    transitionDelay: `${delay}ms`,
                    opacity: animate ? 1 : 0,
                    transform: animate ? 'translateX(0)' : 'translateX(-18px)',
                  }}
                >
                  {char === ' ' ? ' ' : char}
                </span>
              );
            })}
          </div>
        );
      })}
    </h1>
  );
};
