import React from "react";
import Section from "../../common/Section";
import ImageBlock from "../../common/ImageBlock";
import Card from "../../common/Card";
import { ASSETS } from "../../../utils/constants";
import { motion } from "framer-motion";
import "../../../styles/globals.css";

export default function AboutPage() {
  // Values data matching the design
  const valuesData = [
    {
      title: "Safety First",
      description:
        "We prioritize the safety and well-being of our seafarers and vessels, ensuring full compliance with international maritime standards.",
      icon: ASSETS.A_ICONS[0],
    },
    {
      title: "Integrity",
      description:
        "Transparency, honesty, and trust guide everything we do, from recruitment to daily operations.",
      icon: ASSETS.A_ICONS[1],
    },
    {
      title: "Excellence",
      description:
        "We strive for the highest quality in our services, providing skilled and reliable crews for every voyage.",
      icon: ASSETS.A_ICONS[2],
    },
    {
      title: "Sustainability",
      description:
        "We are committed to protecting the marine environment and promoting responsible practices at sea.",
      icon: ASSETS.A_ICONS[3],
    },
    {
      title: "Partnership",
      description:
        "We believe in long-term relationships, working closely with ship owners, principals, and seafarers to achieve shared success.",
      icon: ASSETS.A_ICONS[4],
    },
    {
      title: "Teamwork",
      description:
        "We know that to remain a successful company we must work together, frequently rise above organizational, geographical, and cultural barriers.",
      icon: ASSETS.A_ICONS[5],
    },
  ];

  return (
    <div className="w-full bg-white overflow-x-hidden">
      {/* Hero Section - RESPONSIVE */}
      <Section
        layout="centered"
        background="default"
        padding="lg"
        margin="none"
        title="About Us"
        className="container mx-auto max-w-7xl 2xl:max-w-[1400px] pt-0"
      >
        <div className="flex flex-col gap-6 sm:gap-8">
          {/* Hero Image - RESPONSIVE */}
          <motion.div
            className="w-full"
            initial={{ y: -100, opacity: 0 }}
            whileInView={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            viewport={{ once: true }}
          >
            <ImageBlock
              src={ASSETS.ABOUT_IMAGES[0]}
              alt="Container ship at port with stacked containers"
              aspectRatio="video"
              rounded="2xl"
              shadow="lg"
              className="w-full h-[300px] sm:h-[400px] md:h-[500px] lg:h-[596px] 2xl:h-[700px] object-cover"
              loading="lazy"
            />
          </motion.div>

          {/* Hero Text - RESPONSIVE */}
          <motion.div
            className="w-full space-y-4 sm:space-y-6 px-4 lg:px-0"
            initial={{ y: 100, opacity: 0 }}
            whileInView={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            viewport={{ once: true }}
          >
            <div className="text-[#000000C4] space-y-2">
              <p className="font-normal text-base sm:text-lg md:text-xl lg:text-2xl xl:text-[28px] 2xl:text-3xl px-2 sm:px-4 !leading-relaxed text-center">
                We are certified manning agent based in Port Said, Egypt. We can
                provide you with the best crewing services employing Egyptians.
                All our seamen are thoroughly checked for authenticity of their
                certificates/licenses and are fully equipped with STCW 1995 as
                amended 1997.
              </p>
              <p className="font-normal text-base sm:text-lg md:text-xl lg:text-2xl xl:text-[28px] 2xl:text-3xl px-2 sm:px-4 !leading-relaxed text-center">
                We provide crewing services for any flag state and closely
                monitor crew performance through confidential reports. We also
                handle all travel and vessel arrangements to ensure smooth crew
                relief without issues.
              </p>
            </div>
          </motion.div>
        </div>
      </Section>

      {/* Vision Section - RESPONSIVE */}
      <Section
        layout="split"
        background="default"
        padding="lg"
        margin="sm"
        className="container mx-auto max-w-7xl 2xl:max-w-[1400px] flex flex-col lg:flex-row items-center justify-center gap-6 sm:gap-8 md:gap-12 lg:gap-16"
      >
        {/* Vision Image - RESPONSIVE */}
        <motion.div
          className="w-full lg:w-1/2 aspect-square"
          initial={{ x: -100, opacity: 0 }}
          whileInView={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          viewport={{ once: true }}
        >
          <ImageBlock
            src={ASSETS.ABOUT_IMAGES[1]}
            alt="Aerial view of ship on blue ocean"
            aspectRatio="square"
            rounded="2xl"
            shadow="md"
            className="w-full h-full object-cover"
            loading="lazy"
          />
        </motion.div>

        {/* Vision Content - RESPONSIVE */}
        <motion.div
          className="w-full lg:w-1/2 space-y-4 sm:space-y-6 px-4 lg:px-0"
          initial={{ x: 100, opacity: 0 }}
          whileInView={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          viewport={{ once: true }}
        >
          <h2 className="font-semibold text-xl sm:text-2xl md:text-3xl lg:text-4xl !leading-tight text-[#000000C4] text-center">
            Our Vision
          </h2>
          <p className="font-normal text-base sm:text-lg md:text-xl lg:text-2xl xl:text-[24px] !leading-relaxed text-[#000000C4] text-center px-4 sm:px-8 md:px-12 lg:px-16 xl:px-24">
            At Sakr Manning Agency, our vision is to be a leading provider of
            marine crews for the international shipping industry, contributing
            to the growth of the national economy and foreign trade. We believe
            that excellence comes from the quality of people we provide,
            offering our clients a highly professional workforce and our crews a
            safe, high-quality work environment.
          </p>
        </motion.div>
      </Section>

      {/* Values Section - RESPONSIVE */}
      <Section
        layout="centered"
        background="default"
        padding="lg"
        title="Our Values"
        className="container mx-auto max-w-7xl 2xl:max-w-[1400px]"
      >
        {/* Values Grid - RESPONSIVE */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8 lg:gap-[35px] px-4 sm:px-6 lg:px-0">
          {valuesData.map((value, index) => (
            <motion.div
              key={index}
              initial={{ x: index % 2 === 0 ? -50 : 50, opacity: 0 }}
              whileInView={{ x: 0, opacity: 1 }}
              transition={{
                duration: 0.8,
                ease: "easeOut",
                delay: index * 0.1,
              }}
              viewport={{ once: true }}
            >
              <Card
                variant="values"
                className="w-full min-h-[180px] sm:min-h-[200px] lg:min-h-[220px] bg-transparent rounded-[22px] border border-[#0065AF] hover:shadow-md transition-shadow duration-300 flex flex-col sm:flex-row items-center justify-center p-4 sm:p-6"
              >
                {/* Icon - RESPONSIVE */}
                <div className="flex-shrink-0 flex items-center justify-center mb-4 sm:mb-0">
                  <img
                    src={value.icon}
                    alt={`${value.title} icon`}
                    className="w-10 h-10 sm:w-12 sm:h-12 md:w-14 md:h-14 object-contain"
                  />
                </div>

                {/* Content - RESPONSIVE */}
                <div className="flex-1 space-y-2 sm:space-y-4 text-center sm:text-left sm:ml-4 md:ml-6">
                  <h3 className="font-medium text-lg sm:text-xl md:text-2xl lg:text-[32px] leading-relaxed text-[#000000C4]">
                    {value.title}
                  </h3>
                  <p className="font-normal text-sm sm:text-base md:text-lg lg:text-xl xl:text-[28px] px-2 sm:px-4 md:px-8 lg:px-12 leading-relaxed text-[#000000C4]/80">
                    {value.description}
                  </p>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>
      </Section>
    </div>
  );
}
