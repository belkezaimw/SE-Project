import Head from "next/head";
import Image from "next/image";
import Header from "../components/header/Header";
import HeroSection from "@/components/hero/Hero";
import Footer from "@/components/footer/footer";
import TestimonialsSection from "@/components/Testimonials";
import FeaturesSection from "@/components/FeaturesSection";
import TopPersonalizedCreations from "@/components/CreationCardProps";
export default function Home() {
  return (
<div>
    <Header />
    <HeroSection/>
    <TopPersonalizedCreations/>
    <FeaturesSection/>
    <TestimonialsSection/>
    <Footer/>
</div>
  );
}
