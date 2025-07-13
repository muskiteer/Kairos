import { HTMLAttributes } from "react";
import Marquee from "./ui/marquee";

function LogoCloud(props: HTMLAttributes<HTMLDivElement>) {
  const partners = [
    "Recall",
    "Vincent",
    "Lit Protocol", 
    "Gemini AI",
    "Kairos",
    "Supabase",
    "Qdrant",
    "CoinGecko",
    "TAAPI"
  ];

  return (
    <div {...props}>
      <p className="text-center text-muted-foreground mb-8">Powered by industry leaders</p>
      <Marquee pauseOnHover className="[--duration:30s]" reverse>
        {partners.map((partner, index) => (
          <div
            key={index}
            className="mx-8 text-2xl md:text-3xl font-bold text-muted-foreground hover:text-foreground transition-colors"
          >
            {partner}
          </div>
        ))}
      </Marquee>
    </div>
  );
}

export default LogoCloud;



