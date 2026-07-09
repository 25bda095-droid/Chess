import React, { useState } from 'react';

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Register submitted:', formData);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900 bg-opacity-95 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0 pointer-events-none">
        <div className="absolute -bottom-[20%] -right-[10%] w-[50%] h-[50%] rounded-full bg-emerald-900 blur-[120px] opacity-30"></div>
        <div className="absolute top-[10%] -left-[10%] w-[40%] h-[60%] rounded-full bg-teal-900 blur-[100px] opacity-20"></div>
      </div>

      <div className="relative z-10 w-full max-w-md p-8 m-4 bg-gray-800 bg-opacity-50 backdrop-blur-xl border border-gray-700 rounded-2xl shadow-2xl">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-extrabold text-white tracking-tight mb-2">Create Account</h1>
          <p className="text-gray-400">Join the ultimate chess community</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5" htmlFor="username">
              Username
            </label>
            <input
              id="username"
              name="username"
              type="text"
              required
              className="w-full px-4 py-2.5 bg-gray-900/50 border border-gray-600 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-white placeholder-gray-500 transition-all duration-300 ease-in-out"
              placeholder="e.g. Kasparov99"
              value={formData.username}
              onChange={handleChange}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5" htmlFor="email">
              Email Address
            </label>
            <input
              id="email"
              name="email"
              type="email"
              required
              className="w-full px-4 py-2.5 bg-gray-900/50 border border-gray-600 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-white placeholder-gray-500 transition-all duration-300 ease-in-out"
              placeholder="player@example.com"
              value={formData.email}
              onChange={handleChange}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              required
              className="w-full px-4 py-2.5 bg-gray-900/50 border border-gray-600 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-white placeholder-gray-500 transition-all duration-300 ease-in-out"
              placeholder="••••••••"
              value={formData.password}
              onChange={handleChange}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5" htmlFor="confirmPassword">
              Confirm Password
            </label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              required
              className="w-full px-4 py-2.5 bg-gray-900/50 border border-gray-600 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-white placeholder-gray-500 transition-all duration-300 ease-in-out"
              placeholder="••••••••"
              value={formData.confirmPassword}
              onChange={handleChange}
            />
          </div>

          <button
            type="submit"
            className="w-full mt-2 flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-bold text-white bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 focus:ring-offset-gray-900 transition-all duration-300 transform hover:-translate-y-0.5"
          >
            Create Account
          </button>
        </form>

        <div className="mt-8 text-center text-sm text-gray-400">
          Already have an account?{' '}
          <a href="#" className="font-medium text-emerald-400 hover:text-emerald-300 transition-colors">
            Sign in
          </a>
        </div>
      </div>
    </div>
  );
};

export default Register;
