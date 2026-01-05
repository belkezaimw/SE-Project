import ProductCard from "./ProductCard";

const products = [
  { title: "AMD RYZEN 9 4K", gradient: "bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900" },
  { title: "CIX GAMING PC 2K", gradient: "bg-gradient-to-br from-orange-600 via-red-600 to-pink-600" },
  { title: "AMD RYZEN 7 2K", gradient: "bg-gradient-to-br from-red-900 via-pink-800 to-purple-900" },
];

const ProductsSection = () => {
  return (
    <section className="bg-[#f5f5f5] py-16 px-6 md:px-12">
      <div className="max-w-5xl mx-auto">
        <h2 className="text-2xl md:text-3xl font-bold text-gray-900 text-center mb-10">
          Top Personalized Creations
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {products.map((product) => (
            <ProductCard key={product.title} title={product.title} gradient={product.gradient} />
          ))}
        </div>
      </div>
    </section>
  );
};

export default ProductsSection;
