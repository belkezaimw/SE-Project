import { ChevronLeft, ChevronRight } from "lucide-react";
import Image from "next/image";
const TestimonialsSection = () => {
  return (
    <section className="bg-[#0a0a1a] py-20 px-4">
      <div className="max-w-6xl mx-auto">
        <p className="text-purple-400 text-sm mb-2">★ Testimonials</p>
        <h2 className="text-2xl md:text-3xl font-bold text-white mb-12">
          What Our Recent Customers Say
        </h2>
        
        <div className="flex flex-col md:flex-row gap-8 items-start">
          {/* PC Image */}
          <Image
                src="/image/riad.png"
                alt="Atlas Workshop Logo"
                width={50}
                height={50}
                priority
              />         
          {/* Testimonial Content */}
          <div className="md:w-2/3">
            <blockquote className="text-xl md:text-2xl text-white font-medium mb-6 leading-relaxed">
              "My custom gaming PC arrived perfectly built and performs amazingly. Support helped me pick the perfect components!"
            </blockquote>
            <p className="text-gray-400 text-sm mb-8 leading-relaxed">
              The team at Atlas helped us find a home that we had only ever imagined. We were very particular about the kind of property we wanted and had high expectations, but Maple delivered beyond what we thought was possible. Their commitment to finding the right home for us was evident in every interaction.
            </p>
            
            <div className="flex items-center justify-between">
              <div>
                <p className="text-white font-semibold">riad Martinez</p>
                <p className="text-gray-500 text-sm">San Jose, South Dakota</p>
              </div>
              
              <div className="flex gap-2">
                <button className="w-10 h-10 rounded-full border border-gray-700 flex items-center justify-center text-gray-400 hover:text-white hover:border-gray-500 transition-colors">
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <button className="w-10 h-10 rounded-full border border-gray-700 flex items-center justify-center text-gray-400 hover:text-white hover:border-gray-500 transition-colors">
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default TestimonialsSection;
