import s from "./Features.module.css";
import iconLink from "../../assets/icon-link.svg";
import iconDiagram from "../../assets/icon-diagram.svg";
import iconSecure from "../../assets/icon-secure.svg";
import iconDeveloper from "../../assets/icon-developer.svg";

const features = [
  {
    title: "Branded links",
    description: "Create memorable links that build trust.",
    icon: iconLink,
  },
  {
    title: "Powerful analytics",
    description: "Track clicks, locations, and referrers in real time.",
    icon: iconDiagram,
  },
  {
    title: "Secure & reliable",
    description: "Enterprise-grade security and 99.9% uptime.",
    icon: iconSecure,
  },
  {
    title: "Developer friendly",
    description: "REST API, webhooks, and easy integrations.",
    icon: iconDeveloper,
  },
];

export default function Features() {
  return (
    <section className={s.features} id="product">
      <div className={s.grid}>
        {features.map((feature) => (
          <article key={feature.title} className={s.card}>
            <div className={s.iconBox}>
              <img src={feature.icon} className={s.icon} />
            </div>
            <h3 className={s.cardTitle}>{feature.title}</h3>
            <p className={s.cardDesc}>{feature.description}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
