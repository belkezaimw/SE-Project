'use client';

import Image from 'next/image';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { useRef, useState, useEffect } from 'react';

export default function TopPersonalizedCreations() {
  const scrollRef = useRef(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(true);
  const [selectedCreation, setSelectedCreation] = useState(null);

  const creations = [
    {
      id: 1,
      image: '/image/pc2.png',
      title: '',
      description: 'High-performance RGB build with RTX 4090'
    },
    {
      id: 2,
      image: '/image/pc3.png',
      title: 'Custom Creator Build',
      description: 'Tailored for creators & gamers'
    },
    {
      id: 3,
      image: '/image/pc5.avif',
      title: 'Pro Workstation',
      description: 'Power for productivity & design'
    },
    {
      id: 4,
      image: '/image/pc4.png',
      title: 'Compact Gaming PC',
      description: 'Mini-ITX powerhouse for small spaces'
    },
    {
      id: 5,
      image: '/image/pc2.png',
      title: 'Streaming Setup',
      description: 'Optimized for content creation'
    },
    {
      id: 6,
      image: '/image/pc2.png',
      title: 'Budget Beast',
      description: 'Maximum performance per dollar'
    }
  ];

  const checkScrollPosition = () => {
    if (scrollRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollRef.current;
      setCanScrollLeft(scrollLeft > 0);
      setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 10);
    }
  };

  useEffect(() => {
    checkScrollPosition();
    const scrollElement = scrollRef.current;
    if (scrollElement) {
      scrollElement.addEventListener('scroll', checkScrollPosition);
      return () => scrollElement.removeEventListener('scroll', checkScrollPosition);
    }
  }, []);

  const scrollLeft = () => {
    scrollRef.current?.scrollBy({ left: -340, behavior: 'smooth' });
  };

  const scrollRight = () => {
    scrollRef.current?.scrollBy({ left: 340, behavior: 'smooth' });
  };

  const handleViewDetails = (creation) => {
    setSelectedCreation(creation);
  };

  const closeModal = () => {
    setSelectedCreation(null);
  };

  return (
    <section className="py-16 bg-gradient-to-b from-gray-900 via-gray-900 to-black text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-4xl md:text-5xl font-bold mb-3 bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            Top Personalized Creations
          </h2>
          <p className="text-gray-400 text-lg">
            Handpicked builds crafted by our community
          </p>
        </div>

        <div className="relative group">
          {canScrollLeft && (
            <button
              onClick={scrollLeft}
              aria-label="Scroll left"
              className="absolute left-0 top-1/2 -translate-y-1/2 z-20 bg-black/70 hover:bg-black/90 rounded-full p-3 opacity-0 group-hover:opacity-100 transition-all duration-300 md:opacity-100 shadow-xl hover:scale-110 border border-gray-700"
            >
              <ChevronLeft className="w-6 h-6" />
            </button>
          )}

          {canScrollRight && (
            <button
              onClick={scrollRight}
              aria-label="Scroll right"
              className="absolute right-0 top-1/2 -translate-y-1/2 z-20 bg-black/70 hover:bg-black/90 rounded-full p-3 opacity-0 group-hover:opacity-100 transition-all duration-300 md:opacity-100 shadow-xl hover:scale-110 border border-gray-700"
            >
              <ChevronRight className="w-6 h-6" />
            </button>
          )}

          <div
            ref={scrollRef}
            className="flex gap-6 overflow-x-auto scroll-smooth snap-x snap-mandatory scrollbar-hide px-2 py-4 -mx-2"
          >
            {creations.map((creation) => (
              <div
                key={creation.id}
                className="w-[320px] flex-shrink-0 snap-center bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl shadow-2xl group/card hover:scale-[1.02] transition-all duration-300 border border-gray-700/50 hover:border-purple-500/50 overflow-hidden"
              >
                <div className="relative w-full h-[180px] overflow-hidden bg-black">
                  <Image
                    src={creation.image}
                    alt={creation.title}
                    width={320}
                    height={180}
                    className="w-full h-full object-cover group-hover/card:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover/card:opacity-100 transition-opacity duration-300" />
                </div>

                <div className="p-5">
                  <h3 className="text-xl font-bold mb-2 group-hover/card:text-blue-400 transition-colors duration-300">
                    {creation.title}
                  </h3>
                  <p className="text-gray-400 text-sm leading-relaxed">
                    {creation.description}
                  </p>
                  
                  <button 
                    onClick={() => handleViewDetails(creation)}
                    className="mt-4 w-full py-2 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg font-semibold hover:from-blue-500 hover:to-purple-500 transition-all duration-300 opacity-0 group-hover/card:opacity-100 transform translate-y-2 group-hover/card:translate-y-0"
                  >
                    View Details
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="flex justify-center gap-2 mt-8">
          {creations.slice(0, 4).map((_, index) => (
            <div
              key={index}
              className="w-2 h-2 rounded-full bg-gray-600 hover:bg-blue-500 transition-colors cursor-pointer"
            />
          ))}
        </div>
      </div>

      {/* Modal */}
      {selectedCreation && (
        <div 
          className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={closeModal}
        >
          <div 
            className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl max-w-2xl w-full border border-gray-700 shadow-2xl overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="relative w-full h-[400px] overflow-hidden bg-black">
              <Image
                src={selectedCreation.image}
                alt={selectedCreation.title}
                width={800}
                height={400}
                className="w-full h-full object-cover"
              />
            </div>
            
            <div className="p-8">
              <h3 className="text-3xl font-bold mb-4 text-white">
                {selectedCreation.title}
              </h3>
              <p className="text-gray-300 text-lg mb-6">
                {selectedCreation.description}
              </p>
              
              <div className="space-y-4 mb-6">
                <div className="flex items-center gap-3 text-gray-400">
                  <span className="w-24 font-semibold">Processor:</span>
                  <span>Intel Core i9-13900K / AMD Ryzen 9 7950X</span>
                </div>
                <div className="flex items-center gap-3 text-gray-400">
                  <span className="w-24 font-semibold">GPU:</span>
                  <span>NVIDIA RTX 4090 24GB</span>
                </div>
                <div className="flex items-center gap-3 text-gray-400">
                  <span className="w-24 font-semibold">RAM:</span>
                  <span>64GB DDR5</span>
                </div>
                <div className="flex items-center gap-3 text-gray-400">
                  <span className="w-24 font-semibold">Storage:</span>
                  <span>2TB NVMe SSD</span>
                </div>
              </div>

              <div className="flex gap-4">
                <button className="flex-1 py-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg font-semibold hover:from-blue-500 hover:to-purple-500 transition-all duration-300">
                  Customize Build
                </button>
                <button 
                  onClick={closeModal}
                  className="px-6 py-3 bg-gray-700 hover:bg-gray-600 rounded-lg font-semibold transition-all duration-300"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <style jsx global>{`
        .scrollbar-hide::-webkit-scrollbar {
          display: none;
        }
        .scrollbar-hide {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
      `}</style>
    </section>
  );
}