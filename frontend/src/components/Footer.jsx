import React from 'react';
import { Link } from 'react-router-dom';
import { FiFacebook, FiTwitter, FiInstagram, FiMail } from 'react-icons/fi';

const Footer = () => {
  return (
    <footer className="bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Company Info */}
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-8 h-8 bg-amber-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold">F</span>
              </div>
              <span className="text-xl font-serif font-bold">FurniCraft</span>
            </div>
            <p className="text-gray-400 mb-4">
              Crafting beautiful furniture that transforms houses into homes since 2010.
            </p>
            <div className="flex space-x-4">
              <a href="#" className="text-gray-400 hover:text-amber-600 transition-colors">
                <FiFacebook size={20} />
              </a>
              <a href="#" className="text-gray-400 hover:text-amber-600 transition-colors">
                <FiTwitter size={20} />
              </a>
              <a href="#" className="text-gray-400 hover:text-amber-600 transition-colors">
                <FiInstagram size={20} />
              </a>
              <a href="#" className="text-gray-400 hover:text-amber-600 transition-colors">
                <FiMail size={20} />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Quick Links</h3>
            <ul className="space-y-2">
              <li><Link to="/" className="text-gray-400 hover:text-amber-600 transition-colors">Home</Link></li>
              <li><Link to="/shop" className="text-gray-400 hover:text-amber-600 transition-colors">Shop</Link></li>
              <li><a href="#" className="text-gray-400 hover:text-amber-600 transition-colors">About Us</a></li>
              <li><a href="#" className="text-gray-400 hover:text-amber-600 transition-colors">Contact</a></li>
              <li><Link to="/analytics" className="text-gray-400 hover:text-amber-600 transition-colors">Analytics</Link></li>
            </ul>
          </div>

          {/* Categories */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Categories</h3>
            <ul className="space-y-2">
              <li><Link to="/shop?category=living" className="text-gray-400 hover:text-amber-600 transition-colors">Living Room</Link></li>
              <li><Link to="/shop?category=bedroom" className="text-gray-400 hover:text-amber-600 transition-colors">Bedroom</Link></li>
              <li><Link to="/shop?category=office" className="text-gray-400 hover:text-amber-600 transition-colors">Office</Link></li>
              <li><Link to="/shop?category=dining" className="text-gray-400 hover:text-amber-600 transition-colors">Dining</Link></li>
              <li><Link to="/shop?category=outdoor" className="text-gray-400 hover:text-amber-600 transition-colors">Outdoor</Link></li>
            </ul>
          </div>

          {/* Newsletter */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Newsletter</h3>
            <p className="text-gray-400 mb-4">
              Subscribe to get special offers, free giveaways, and new product updates.
            </p>
            <form className="flex">
              <input
                type="email"
                placeholder="Enter your email"
                className="flex-1 px-4 py-2 bg-gray-800 border border-gray-700 rounded-l-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent outline-none"
              />
              <button
                type="submit"
                className="bg-amber-600 text-white px-4 py-2 rounded-r-lg hover:bg-amber-700 transition-colors"
              >
                Subscribe
              </button>
            </form>
          </div>
        </div>

        <div className="border-t border-gray-800 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-gray-400 text-sm">
            © 2024 FurniCraft. All rights reserved.
          </p>
          <div className="flex space-x-6 mt-4 md:mt-0">
            <a href="#" className="text-gray-400 hover:text-amber-600 text-sm transition-colors">
              Privacy Policy
            </a>
            <a href="#" className="text-gray-400 hover:text-amber-600 text-sm transition-colors">
              Terms of Service
            </a>
            <a href="#" className="text-gray-400 hover:text-amber-600 text-sm transition-colors">
              Returns & Refunds
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;