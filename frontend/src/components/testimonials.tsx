import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import Marquee from "@/components/ui/marquee";
import React from "react";

const testimonials = [
  {
    id: 1,
    name: "Marcus Chen",
    designation: "Crypto Trader",
    company: "BlockTrade Capital",
    testimonial:
      "Kairos AI has completely transformed my trading strategy. The autonomous agent makes profitable trades while I sleep, and the Vincent policy engine gives me perfect risk control.",
    avatar: "https://randomuser.me/api/portraits/men/1.jpg",
  },
  {
    id: 2,
    name: "Sarah Williams",
    designation: "Portfolio Manager",
    company: "Digital Assets Inc",
    testimonial:
      "The hybrid architecture with vector memory is genius. Kairos learns from every trade and applies past experiences to new opportunities. My returns have increased by 40%.",
    avatar: "https://randomuser.me/api/portraits/women/6.jpg",
  },
  {
    id: 3,
    name: "Alex Rodriguez",
    designation: "DeFi Investor",
    company: "CryptoVentures",
    testimonial:
      "I love how Kairos operates in different modes. Normal mode keeps me in control, while Aggressive mode unleashes full AI autonomy. The Lit Protocol integration is seamless.",
    avatar: "https://randomuser.me/api/portraits/men/3.jpg",
  },
  {
    id: 4,
    name: "Emma Thompson",
    designation: "Algorithmic Trader",
    company: "QuantCrypto Labs",
    testimonial:
      "The real-time market analysis using CoinGecko and TAAPI data is incredibly accurate. Kairos consistently identifies profitable opportunities before the market moves.",
    avatar: "https://randomuser.me/api/portraits/women/4.jpg",
  },
  {
    id: 5,
    name: "David Kim",
    designation: "Crypto Fund Manager",
    company: "Blockchain Capital",
    testimonial:
      "The strategy builder is intuitive and powerful. I can create custom rules that the AI follows perfectly. The dashboard shows exactly why each trade was made.",
    avatar: "https://randomuser.me/api/portraits/men/5.jpg",
  },
  {
    id: 6,
    name: "Luna Nakamura",
    designation: "DeFi Strategist",
    company: "Web3 Innovations",
    testimonial:
      "Kairos' ability to recall similar market situations and learn from past trades is revolutionary. It's like having a crypto trading mentor that never forgets.",
    avatar: "https://randomuser.me/api/portraits/women/2.jpg",
  },
];

const Testimonials = () => (
  <div id="testimonials" className="flex justify-center items-center py-20">
    <div className="h-full w-full">
      <h2 className="mb-12 text-4xl md:text-5xl font-bold text-center tracking-tight px-6">
        What Traders Say About Kairos
      </h2>
      <div className="relative">
        <div className="z-10 absolute left-0 inset-y-0 w-[15%] bg-gradient-to-r from-background to-transparent pointer-events-none" />
        <div className="z-10 absolute right-0 inset-y-0 w-[15%] bg-gradient-to-l from-background to-transparent pointer-events-none" />
        
        <Marquee pauseOnHover className="[--duration:40s]" repeat={2}>
          {testimonials.map((testimonial) => (
            <TestimonialCard key={testimonial.id} testimonial={testimonial} />
          ))}
        </Marquee>
        
        <Marquee pauseOnHover reverse className="mt-4 [--duration:40s]" repeat={2}>
          {testimonials.map((testimonial) => (
            <TestimonialCard key={`reverse-${testimonial.id}`} testimonial={testimonial} />
          ))}
        </Marquee>
      </div>
    </div>
  </div>
);

const TestimonialCard = ({ testimonial }: { testimonial: typeof testimonials[0] }) => (
  <div className="min-w-96 max-w-sm bg-accent rounded-xl p-6 mx-4 border shadow-sm">
    <div className="flex items-center justify-between mb-4">
      <div className="flex items-center gap-4">
        <Avatar className="w-12 h-12">
          <AvatarImage src={testimonial.avatar} alt={testimonial.name} />
          <AvatarFallback className="text-lg font-medium bg-primary text-primary-foreground">
            {testimonial.name.charAt(0)}
          </AvatarFallback>
        </Avatar>
        <div>
          <p className="text-lg font-semibold">{testimonial.name}</p>
          <p className="text-sm text-muted-foreground">{testimonial.designation}</p>
          <p className="text-xs text-muted-foreground font-medium">{testimonial.company}</p>
        </div>
      </div>
      <div className="flex gap-1">
        {[...Array(5)].map((_, i) => (
          <svg key={i} className="w-4 h-4 fill-yellow-400" viewBox="0 0 20 20">
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
        ))}
      </div>
    </div>
    <blockquote className="text-[15px] leading-relaxed text-foreground">
      "{testimonial.testimonial}"
    </blockquote>
  </div>
);

export default Testimonials;
