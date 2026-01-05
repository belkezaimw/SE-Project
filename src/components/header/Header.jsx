"use client";

import Link from "next/link";
import Image from "next/image";
const navLinks = [
  { name: "PC Builder", href: "/" },
  { name: "Products", href: "/products" },
  { name: "Components", href: "/components" },
  { name: "About", href: "/about" },
];

const Navbar = () => {
  return (
    <nav className="absolute top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-4 md:px-12 backdrop-blur-sm">
      {/* Logo */}
<Image
      src="/image/logo.svg"
      alt="Atlas Workshop Logo"
      width={40}
      height={40}
      priority
    />

      {/* Desktop Navigation */}
      <div className="hidden md:flex items-center gap-8 text-sm text-gray-300">
        {navLinks.map((link) => (
          <Link
            key={link.name}
            href={link.href}
            className="relative hover:text-white transition-colors after:absolute after:left-0 after:-bottom-1 after:h-[1px] after:w-0 after:bg-white after:transition-all hover:after:w-full"
          >
            {link.name}
          </Link>
        ))}
      </div>

      {/* Mobile Menu Button (placeholder) */}
      <button
        className="md:hidden text-white text-xl"
        aria-label="Open menu"
      >
        ☰
      </button>
    </nav>
  );
};

export default Navbar;
