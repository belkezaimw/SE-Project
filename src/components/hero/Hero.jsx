import Image from "next/image";

const HeroSection = () => {
  return (
    <section className="relative min-h-screen bg-gradient-to-b from-[#0a0a1a] via-[#0f0f2a] to-[#0a0a1a] flex flex-col items-center justify-center px-4 pt-20 pb-12 overflow-hidden">
      {/* Background glow effects */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-600/20 rounded-full blur-[120px]" />
      <div className="absolute top-1/3 right-1/4 w-72 h-72 bg-blue-500/15 rounded-full blur-[100px]" />
      
      <div className="relative z-10 text-center max-w-4xl mx-auto">
        <h1 className="text-4xl md:text-6xl font-bold text-white mb-4 tracking-tight">
          HIGH PERFORMANCE
          <br />
          COMPONENTS AWAITS FOR YOU
        </h1>
        <p className="text-gray-400 text-sm md:text-base mb-8 max-w-xl mx-auto">
          Customize every component to match your gaming needs and budget. 100% compatibility guaranteed.
        </p>
        <button className="bg-purple-600 hover:bg-purple-700 text-white px-8 py-3 rounded-full font-medium transition-all hover:shadow-lg hover:shadow-purple-500/30">
          Start Building
        </button>
      </div>

      {/* PC Image with ellipse */}
      <div className="relative z-10 mt-8 md:mt-12">
                    <Image
                  src="/image/pc1.png"
                  alt="Atlas Workshop Logo"
                  width={400}
                  height={400}
                  priority
                />
        
        <p className="text-center text-gray-400 text-sm mt-8 tracking-widest">
          BILD WITH 4K RGB
        </p>
      </div>
    </section>
  );
};

export default HeroSection;
