import { Shield, Truck, Headphones } from "lucide-react";

const features = [
  {
    icon: Shield,
    title: "COMPATIBILITY GUARANTEED",
    description: "Our system automatically checks component compatibility so you don't have to worry about mismatched parts."
  },
  {
    icon: Truck,
    title: "FAST & FREE SHIPPING",
    description: "Free expedited shipping on all orders. Most systems ship within 3 business days after configuration."
  },
  {
    icon: Headphones,
    title: "LIFETIME SUPPORT",
    description: "Our experts are available 24/7 to help with any questions or issues with your custom build."
  }
];

const FeaturesSection = () => {
  return (
    <section className="bg-[#0a0a1a] py-20 px-4">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-2xl md:text-3xl font-bold text-white text-center mb-16">
          Why Build With Atlas Workshop
        </h2>
        
        <div className="grid md:grid-cols-3 gap-8 mb-12">
          {features.map((feature, index) => (
            <div key={index} className="text-center p-6 rounded-xl border border-gray-800 bg-gray-900/30">
              <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-purple-600/20 flex items-center justify-center">
                <feature.icon className="w-6 h-6 text-purple-400" />
              </div>
              <h3 className="text-sm font-semibold text-white mb-2 tracking-wide">
                {feature.title}
              </h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
        
        <div className="text-center">
          <button className="bg-purple-600 hover:bg-purple-700 text-white px-8 py-3 rounded-full font-medium transition-all hover:shadow-lg hover:shadow-purple-500/30">
            Start Building
          </button>
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;
