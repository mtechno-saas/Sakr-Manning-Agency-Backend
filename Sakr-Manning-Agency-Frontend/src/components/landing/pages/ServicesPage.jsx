import React from "react";
import Section from "../../common/Section";
import ImageBlock from "../../common/ImageBlock";
import Button from "../../common/Button";
import { ASSETS } from "../../../utils/constants";
import { motion } from "framer-motion";
import "../../../styles/globals.css";

const ServicesPage = ({ onNavigate }) => {
  const services = [
    "Suez Canal Transit Agent",
    "Crew search and selection",
    "Crew conference",
    "Crewing System Update",
    "Crew P&I insurance",
    "Health insurance",
    "Organizing flights bookings",
    "Training & Cadet Programs",
  ];

  const ServiceTag = ({ service }) => (
    <div className="flex justify-center items-center px-4 sm:px-6 md:px-[10px] py-3 sm:py-4 md:py-[10px] 2xl:py-5 2xl:px-8 gap-[10px] border border-[rgba(36,119,195,0.51)] rounded-[22px] 2xl:rounded-[30px] text-center min-h-[53px] 2xl:min-h-[70px] w-full">
      <span className="font-medium text-base sm:text-lg md:text-xl lg:text-[22px] 2xl:text-3xl leading-[150%] text-[rgba(0,0,0,0.77)]">
        {service}
      </span>
    </div>
  );

  return (
    <div className="w-full overflow-x-hidden">
      {/* Hero Section - Split Layout RESPONSIVE */}
      <Section
        padding="lg"
        margin="none"
        className="pt-8 sm:pt-10 md:pt-12 px-4 sm:px-6 md:px-8"
      >
        <div className="flex flex-col lg:flex-row items-center justify-center gap-6 sm:gap-8 md:gap-10 lg:gap-[41px] w-full max-w-7xl 2xl:max-w-[1400px] mx-auto">
          {/* Image Block - RESPONSIVE - Fits text content height */}
          <motion.div
            className="w-full lg:w-1/2 flex-shrink-0"
            initial={{ x: -100, y: -100, opacity: 0 }}
            whileInView={{ x: 0, y: 0, opacity: 1 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            viewport={{ once: true }}
          >
            <ImageBlock
              src={ASSETS.SERVICES}
              objectFit="cover"
              alt="Services hero image"
              aspectRatio="auto"
              rounded="xl"
              className="w-full h-auto max-h-[450px] lg:max-h-[500px] xl:max-h-[550px] 2xl:max-h-[650px]"
              loading="lazy"
              placeholder={
                <div className="bg-gray-300 w-full h-full flex items-center justify-center text-gray-500 rounded-[22px]">
                  Services Hero Image
                </div>
              }
            />
          </motion.div>

          {/* Text Content - RESPONSIVE - Natural height */}
          <motion.div
            className="w-full lg:w-1/2 flex flex-col justify-center gap-4 sm:gap-6 px-4 sm:px-6 md:px-8 lg:px-12 text-center"
            initial={{ x: 100, y: -100, opacity: 0 }}
            whileInView={{ x: 0, y: 0, opacity: 1 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            viewport={{ once: true }}
          >
            <h1 className="w-full font-semibold text-xl sm:text-2xl md:text-3xl lg:text-[32px] 2xl:text-[40px] leading-[148.01%] text-black">
              Services
            </h1>
            <p className="w-full font-normal text-sm sm:text-base md:text-lg lg:text-xl xl:text-[22px] 2xl:text-[26px] leading-[180%] md:leading-[207%] text-[rgba(0,0,0,0.77)]">
              Sakr Manning Agency recognizes seafarers as our Principals'
              greatest asset, essential to service quality and reputation. We
              are committed to meeting your needs with a strong focus on
              customer satisfaction. Through continuous analysis, appraisal, and
              training, we ensure constant improvement in proficiency,
              effectiveness, and cost efficiency. In addition, we provide a
              dedicated office to represent your identity and strengthen
              relationships with your crew.
            </p>
          </motion.div>
        </div>
      </Section>
      {/* Service Tags Section - RESPONSIVE */}
      <Section
        padding="lg"
        margin="none"
        maxWidth="xl"
        title="Crewing & Maritime Support Services"
        className="text-center px-4 sm:px-6 md:px-8"
      >
        <div className="flex flex-col items-start gap-4 sm:gap-6 md:gap-[25px] w-full">
          {/* Service Tags in Rows - RESPONSIVE GRID */}
          {[0, 2, 4, 6].map((startIndex) => (
            <div
              key={startIndex}
              className="flex flex-col md:flex-row items-center gap-4 md:gap-8 lg:gap-12 xl:gap-[71px] 2xl:gap-24 w-full"
            >
              {services
                .slice(startIndex, startIndex + 2)
                .map((service, index) => (
                  <motion.div
                    key={service}
                    className="w-full md:flex-1"
                    initial={{
                      x: (startIndex + index) % 2 === 0 ? -50 : 50,
                      opacity: 0,
                    }}
                    whileInView={{ x: 0, opacity: 1 }}
                    transition={{
                      duration: 0.8,
                      ease: "easeOut",
                      delay: (startIndex + index) * 0.1,
                    }}
                    viewport={{ once: true }}
                  >
                    <ServiceTag service={service} />
                  </motion.div>
                ))}
            </div>
          ))}
        </div>
      </Section>
      {/* CTA Section - RESPONSIVE */}
      <Section
        padding="md"
        margin="none"
        className="relative w-full max-w-[1250px] 2xl:max-w-[1500px] min-h-[200px] sm:min-h-[220px] md:min-h-[235px] 2xl:min-h-[280px] mx-auto px-4 sm:px-6 md:px-8 mb-12 sm:mb-14 md:mb-16"
      >
        <div className="w-full h-full bg-gradient-to-r from-[#DBE9F5] to-[#AFD1EE] rounded-[22px] flex flex-col items-center justify-center gap-8 sm:gap-10 md:gap-[50px] py-8 sm:py-10 md:py-12 px-4 sm:px-6">
          <h2 className="font-semibold text-xl sm:text-2xl md:text-3xl lg:text-[32px] leading-[140%] md:leading-[48px] text-[#0065AF] text-center">
            JOIN TO SAKR MANNING AGENCY
          </h2>

          <Button
            variant="outlined"
            size="lg"
            onClick={() => onNavigate("contact")}
            className="flex items-center px-4 sm:px-6 md:px-[16px] py-3 sm:py-4 md:py-[12px] 2xl:py-5 2xl:px-8 w-auto h-10 sm:h-11 md:h-[47px] 2xl:h-16 font-medium text-sm sm:text-base 2xl:text-xl border border-[#0065AF] rounded-[22px] 2xl:rounded-[30px] bg-transparent hover:bg-[#0065AF] hover:text-white transition-colors"
          >
            Contact Us
          </Button>
        </div>
      </Section>
    </div>
  );
};

export default ServicesPage;
