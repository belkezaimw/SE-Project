import { Twitter, Linkedin, Instagram } from "lucide-react";

const Footer = () => {
  return (
    <footer className="bg-[#0a0a1a] border-t border-gray-800 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          {/* Logo */}
          <div className="text-white font-bold text-lg tracking-wide">
            FORGE WORKSHOP
          </div>
          
          {/* Navigation */}
          <nav className="flex flex-wrap items-center justify-center gap-8 text-sm">
            <a href="#" className="text-gray-400 hover:text-white transition-colors">
              PC Builder
            </a>
            <a href="#" className="text-gray-400 hover:text-white transition-colors">
              Prebuilts
            </a>
            <a href="#" className="text-gray-400 hover:text-white transition-colors">
              Components
            </a>
            <a href="#" className="text-gray-400 hover:text-white transition-colors">
              About
            </a>
          </nav>
          
          {/* Social Icons */}
          <div className="flex items-center gap-4">
            <a href="#" className="text-gray-400 hover:text-white transition-colors">
              <Twitter className="w-5 h-5" />
            </a>
            <a href="#" className="text-gray-400 hover:text-white transition-colors">
              <Instagram className="w-5 h-5" />
            </a>
            <a href="#" className="text-gray-400 hover:text-white transition-colors">
              <Linkedin className="w-5 h-5" />
            </a>
          </div>
        </div>
        
        <div className="mt-8 pt-6 border-t border-gray-800 text-center">
          <p className="text-gray-500 text-sm">
            © 2026 Forge Workshop. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
