import React from 'react';

// Simple UI component exports for the OCR feature
// These are basic implementations - can be enhanced with proper styling

export const Card: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <div className={`bg-white shadow rounded-lg ${className}`}>{children}</div>
);

export const CardHeader: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <div className={`px-6 py-4 border-b ${className}`}>{children}</div>
);

export const CardTitle: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <h3 className={`text-lg font-semibold ${className}`}>{children}</h3>
);

export const CardContent: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <div className={`px-6 py-4 ${className}`}>{children}</div>
);

export const Button: React.FC<{
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'default' | 'outline' | 'destructive';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  className?: string;
}> = ({ children, onClick, variant = 'default', size = 'md', disabled = false, className = '' }) => {
  const variants = {
    default: 'bg-blue-600 text-white hover:bg-blue-700',
    outline: 'border border-gray-300 hover:bg-gray-50',
    destructive: 'bg-red-600 text-white hover:bg-red-700',
  };
  
  const sizes = {
    sm: 'px-3 py-1 text-sm',
    md: 'px-4 py-2',
    lg: 'px-6 py-3 text-lg',
  };
  
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`rounded font-medium transition-colors ${variants[variant]} ${sizes[size]} ${disabled ? 'opacity-50 cursor-not-allowed' : ''} ${className}`}
    >
      {children}
    </button>
  );
};

export const Badge: React.FC<{
  children: React.ReactNode;
  variant?: 'default' | 'secondary' | 'outline' | 'destructive' | 'success';
  className?: string;
}> = ({ children, variant = 'default', className = '' }) => {
  const variants = {
    default: 'bg-gray-100 text-gray-800',
    secondary: 'bg-blue-100 text-blue-800',
    outline: 'border border-gray-300',
    destructive: 'bg-red-100 text-red-800',
    success: 'bg-green-100 text-green-800',
  };
  
  return (
    <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded ${variants[variant]} ${className}`}>
      {children}
    </span>
  );
};

export const Alert: React.FC<{
  children: React.ReactNode;
  variant?: 'default' | 'destructive';
  className?: string;
}> = ({ children, variant = 'default', className = '' }) => {
  const variants = {
    default: 'bg-blue-50 border-blue-200 text-blue-800',
    destructive: 'bg-red-50 border-red-200 text-red-800',
  };
  
  return (
    <div className={`border rounded-lg p-4 ${variants[variant]} ${className}`}>
      {children}
    </div>
  );
};

export const AlertDescription: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <div className={`text-sm ${className}`}>{children}</div>
);

export const ScrollArea: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <div className={`overflow-auto ${className}`}>{children}</div>
);

export const Progress: React.FC<{ value: number; className?: string }> = ({ value, className = '' }) => (
  <div className={`w-full bg-gray-200 rounded-full h-2 ${className}`}>
    <div className="bg-blue-600 h-2 rounded-full transition-all" style={{ width: `${value}%` }} />
  </div>
);

export const Tabs: React.FC<{
  children: React.ReactNode;
  value: string;
  onValueChange: (value: string) => void;
  className?: string;
}> = ({ children, value, onValueChange, className = '' }) => {
  return (
    <div className={className}>
      {React.Children.map(children, child => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child as any, { activeTab: value, onTabChange: onValueChange });
        }
        return child;
      })}
    </div>
  );
};

export const TabsList: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <div className={`flex border-b ${className}`}>{children}</div>
);

export const TabsTrigger: React.FC<{
  children: React.ReactNode;
  value: string;
  className?: string;
  activeTab?: string;
  onTabChange?: (value: string) => void;
}> = ({ children, value, className = '', activeTab, onTabChange }) => (
  <button
    onClick={() => onTabChange?.(value)}
    className={`px-4 py-2 font-medium transition-colors ${
      activeTab === value ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-600 hover:text-gray-800'
    } ${className}`}
  >
    {children}
  </button>
);

export const TabsContent: React.FC<{
  children: React.ReactNode;
  value: string;
  className?: string;
  activeTab?: string;
}> = ({ children, value, className = '', activeTab }) => {
  if (activeTab !== value) return null;
  return <div className={`mt-4 ${className}`}>{children}</div>;
};