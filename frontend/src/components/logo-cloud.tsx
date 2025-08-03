import { HTMLAttributes } from "react";
import Marquee from "./ui/marquee";

function LogoCloud(props: HTMLAttributes<HTMLDivElement>) {
  const partners = [
    "Kairos AI",
    "Recall",
    "Vincent AI",
    "Lit Protocol", 
    "Gemini AI",
    "Supabase",
    "CoinGecko",
    "Uniswap",
  ];

  return (
    <div {...props} className="w-full overflow-hidden">
      <p className="text-center text-muted-foreground mt-8 md:mt-12 mb-4 md:mb-8 text-xs md:text-base px-4">Powered by industry leaders</p>
      <div className="w-full overflow-hidden">
        <Marquee pauseOnHover className="[--duration:15s] md:[--duration:30s]" reverse>
          {partners.map((partner, index) => (
            <div
              key={index}
              className="mx-2 md:mx-6 lg:mx-8 text-sm md:text-xl lg:text-2xl xl:text-3xl font-semibold md:font-bold text-muted-foreground hover:text-foreground transition-colors whitespace-nowrap"
            >
              {partner}
            </div>
          ))}
        </Marquee>
      </div>
    </div>
  );
}

export default LogoCloud;



