import React, { useState, useEffect, useRef } from "react";
import Section from "../../common/Section";
import Button from "../../common/Button";
import Card from "../../common/Card";
import ImageBlock from "../../common/ImageBlock";
import { ASSETS } from "../../../utils/constants";
import { motion } from "framer-motion";
import "../../../styles/globals.css";
import { useNavigate } from "react-router-dom";
import { jobOrdersApi } from "../../../services/Dashboard/jobOrdersApi";
import InfiniteTicker from "../../common/InfiniteTicker";


// ── Fallback shown while loading or when the API returns nothing ──────────
const FALLBACK_JOBS = [
  { title: "Deck Officer", text: "Experienced officer required for international routes" },
  { title: "Chief Engineer", text: "Senior engineer for bulk carrier fleet" },
  { title: "AB Seaman", text: "Able seaman for container vessel" },
  { title: "Cook / Catering Staff", text: "Catering positions available across our fleet" },
  { title: "Electrician", text: "Marine electrician for offshore assignments" },
];

const HomePage = ({ user, onOpenForm, onNavigate }) => {
  const navigate = useNavigate();
  const [currentSlide, setCurrentSlide] = useState(0);
  const [heroImageLoaded, setHeroImageLoaded] = useState(false);

  // ── Live vacancies state ─────────────────────────────────────────────────
  const [jobs, setJobs] = useState(FALLBACK_JOBS);
  const [vacanciesLoading, setVacanciesLoading] = useState(true);

  const slides = [
    {
      services: [
        "Suez Canal Transit Agent",
        "Crew Search and Selection",
        "Crew Conference",
        "Crewing System Update",
      ],
      background: ASSETS.SLIDER_IMAGES[0],
    },
    {
      services: [
        "Crew P&I Insurance",
        "Health Insurance",
        "Organizing Flights Bookings",
        "Training & Cadet Programs",
      ],
      background: ASSETS.SLIDER_IMAGES[1],
    },
    {
      services: [
        "Crew Recruitment & Management",
        "Crew Performance Monitoring",
        "Travel & Logistics Arrangements",
        "Dedicated Principal Support",
      ],
      background: ASSETS.SLIDER_IMAGES[2],
    },
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % slides.length);
    }, 100000);
    return () => clearInterval(interval);
  }, [slides.length]);

  // ── Fetch open job positions from the backend ───────────────────────────
  useEffect(() => {
    let cancelled = false;
    const loadVacancies = async () => {
      try {
        setVacanciesLoading(true);
        // We fetch positions directly as they represent the "Vacancies" for seafarers
        const response = await jobOrdersApi.getJobPositions();
        const list = Array.isArray(response) ? response : (response.results || response.job_positions || []);

        if (!cancelled && list.length > 0) {
          // Filter out jobs where rank_name is null, undefined, or empty
          const validPositions = list.filter(
            (p) => p && p.rank_name !== null && p.rank_name !== undefined && p.rank_name !== ""
          );

          if (validPositions.length > 0) {
            const mapped = validPositions.map((p) => ({
              title: p.rank_name,
              salaryMin: p.salary_min,
              salaryMax: p.salary_max,
              currency: p.currency || 'USD',
              duration: p.contract_duration_months,
              quantity: p.quantity,
              remarks: p.remarks,
              id: p.id,
            }));
            setJobs(mapped);
          }
        }
      } catch (err) {
        // Silently fall back to the static list
        console.warn("Could not load job positions from API:", err.message);
      } finally {
        if (!cancelled) setVacanciesLoading(false);
      }
    };

    loadVacancies();
    return () => { cancelled = true; };
  }, []);

  const jobsRef = useRef(null);

  const scrollToJobs = () => {
    if (jobsRef.current) {
      jobsRef.current.scrollIntoView({ behavior: "smooth" });
    }
  };

  const handleHeroImageLoad = () => {
    setHeroImageLoaded(true);
  };

  const handleHeroImageError = () => {
    setHeroImageLoaded(false);
  };

  return (
    <div className="w-full mx-auto bg-white">
      {/* Hero Section - RESPONSIVE */}
      <Section
        padding="none"
        layout="custom"
        margin="none"
        className="w-full h-[70vh] sm:h-[80vh] lg:h-[85vh] 2xl:h-[90vh] overflow-hidden rounded-none md:rounded-3xl 2xl:rounded-none relative mx-0 2xl:mx-0"
      >
        <div className="relative w-full h-full">
          <ImageBlock
            src={ASSETS.HOME_IMAGES[0]}
            alt="Hero Background"
            aspectRatio="auto"
            objectFit="cover"
            rounded="none"
            className="w-full h-full"
            onLoad={handleHeroImageLoad}
            onError={handleHeroImageError}
            loading="eager"
            overlay={
              heroImageLoaded ? (
                <div className="relative w-full h-full flex flex-col justify-center">
                  {/* Buttons - RESPONSIVE */}
                  <div className="mx-auto z-[999] mt-[-24px] hero-polished-card">
                    <Button
                      onClick={onOpenForm}
                      variant="primary"
                      className="w-28 h-9 sm:w-32 sm:h-10 md:w-42 md:h-11 lg:w-48 lg:h-12 2xl:w-48 2xl:h-14 text-xs sm:text-sm md:text-base 2xl:text-lg font-medium"
                    >
                      Online Form
                    </Button>
                    <Button
                      onClick={scrollToJobs}
                      variant="outlined"
                      className="w-28 h-9 sm:w-32 sm:h-10 md:w-42 md:h-11 lg:w-48 lg:h-12 2xl:w-48 2xl:h-14 text-xs sm:text-sm md:text-base 2xl:text-lg font-medium"
                    >
                      Open Vacancies
                    </Button>
                  </div>

                  {/* Hero Text - RESPONSIVE */}
                  <div className="flex flex-col items-start justify-start px-4 sm:px-6 md:px-12 lg:px-24 text-center mt-6 sm:mt-8 md:mt-10">
                    <motion.h1
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{
                        duration: 0.8,
                        ease: "easeOut",
                        delay: 0.2,
                      }}
                      className="font-semibold text-xl sm:text-2xl md:text-3xl lg:text-4xl xl:text-5xl 2xl:text-7xl leading-tight text-white mb-3 sm:mb-4 2xl:mb-6"
                    >
                      Welcome To Sakr Manning Agency
                    </motion.h1>

                    <motion.p
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{
                        duration: 0.8,
                        ease: "easeOut",
                        delay: 0.4,
                      }}
                      className="font-medium text-base sm:text-lg md:text-xl lg:text-2xl xl:text-3xl 2xl:text-5xl leading-tight text-white opacity-90"
                    >
                      For Recruiting Egyptian Labor Abroad
                    </motion.p>
                  </div>

                  {/* Services Tags - RESPONSIVE with horizontal scroll on mobile */}
                  <div className="w-full px-4 sm:px-6 md:px-12 mb-6 sm:mb-8 md:mb-10 mt-auto">
                    <div className="overflow-x-auto md:overflow-visible scrollbar-hide">
                      <div className="flex justify-center items-center gap-4 sm:gap-6 md:gap-8 lg:gap-12 xl:gap-20 min-w-max md:min-w-0">
                        {[
                          "Recruiting Agency",
                          "Crew search and selection",
                          "Crewing system",
                          "Health insurance",
                        ].map((service, index) => (
                          <motion.span
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{
                              duration: 0.8,
                              ease: "easeOut",
                              delay: 0.4,
                            }}
                            key={index}
                            className="text-xs sm:text-sm md:text-base lg:text-lg xl:text-xl font-medium text-white/70 whitespace-nowrap"
                          >
                            {service}
                          </motion.span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="relative w-full h-full"></div>
              )
            }
          />
        </div>
      </Section>

      {/* About Section - RESPONSIVE */}
      <Section
        layout="split"
        background="default"
        padding="lg"
        margin="none"
        className="container mx-auto w-full max-w-7xl 2xl:max-w-[1600px] flex flex-col lg:flex-row items-center justify-center gap-6 md:gap-8 lg:gap-12 2xl:gap-20"
      >
        {/* About Image */}
        <motion.div
          className="w-full lg:w-1/2 aspect-square 2xl:aspect-[4/3]"
          initial={{ x: -100, opacity: 0 }}
          whileInView={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          viewport={{ once: true }}
        >
          <ImageBlock
            src={ASSETS.HOME_IMAGES[1]}
            alt="Port Said maritime view with ships"
            className="w-full object-cover rounded-2xl md:rounded-3xl"
            aspectRatio="square"
            loading="lazy"
          />
        </motion.div>

        {/* About Content */}
        <motion.div
          className="w-full lg:w-1/2 space-y-4 md:space-y-6 px-4 lg:px-0"
          initial={{ x: 100, opacity: 0 }}
          whileInView={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          viewport={{ once: true }}
        >
          <h2 className="font-semibold text-xl sm:text-2xl md:text-3xl lg:text-4xl xl:text-5xl 2xl:text-6xl leading-tight text-black/90 text-center">
            About Us
          </h2>
          <p className="font-semibold text-base sm:text-lg md:text-xl lg:text-2xl xl:text-3xl 2xl:text-4xl text-center leading-relaxed text-black/80">
            We are a certified/licensed manning agent based in Port Said, Egypt,
            fully compliant with MLC 2006 & STCW 2010 regulations.
          </p>
          <p className="font-normal text-base sm:text-lg md:text-xl lg:text-2xl xl:text-3xl 2xl:text-4xl text-center leading-relaxed text-black/80">
            We provide the best crewing services employing Egyptian seafarers.
            All our seamen are thoroughly verified for the authenticity of their
            certificates/licenses and are fully equipped to meet international
            standards.
          </p>

          <div className="pt-4 md:pt-6 flex justify-center">
            <Button
              onClick={() => onNavigate("about")}
              variant="outlined"
              className="px-8 sm:px-10 md:px-12 py-2.5 sm:py-3 rounded-3xl bg-transparent transition-colors w-auto h-10 sm:h-11 md:h-12"
            >
              <span className="font-medium text-sm sm:text-base">
                Read more
              </span>
            </Button>
          </div>
        </motion.div>
      </Section>

      {/* Services Section - RESPONSIVE */}
      <Section
        layout="centered"
        background="image"
        padding="lg"
        textAlign="center"
        backgroundImage={slides[currentSlide].background}
        className="relative min-h-[60vh] sm:min-h-[70vh] md:min-h-[80vh] 2xl:min-h-[85vh] rounded-none md:rounded-3xl 2xl:rounded-none overflow-hidden mx-auto flex flex-col justify-center"
      >
        {/* Dark Overlay */}
        <div className="absolute inset-0 bg-black/50"></div>

        <div className="relative z-10 flex flex-col gap-8 sm:gap-12 md:gap-16 mx-auto w-full px-4 sm:px-6 md:px-8">
          {/* Services Content */}
          <div className="flex flex-col items-center gap-8 sm:gap-12 md:gap-16">
            {/* Title */}
            <h2 className="text-white text-xl sm:text-2xl md:text-3xl lg:text-4xl font-medium">
              Our Services
            </h2>

            {/* Services Grid - RESPONSIVE */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6 md:gap-8 lg:gap-12 w-full max-w-5xl">
              {slides[currentSlide].services.map((service, index) => (
                <Card
                  key={index}
                  variant="service"
                  className="min-h-[60px] sm:min-h-[70px] md:min-h-[80px] flex justify-center items-center px-4 py-3 border border-white rounded-2xl md:rounded-3xl hover:bg-white/10 transition-colors duration-200"
                >
                  <p className="font-normal text-sm sm:text-base md:text-lg lg:text-xl xl:text-2xl text-center text-white">
                    {service}
                  </p>
                </Card>
              ))}
            </div>

            {/* Read More Button */}
            <Button
              onClick={() => onNavigate("services")}
              variant="outlined"
              className="px-8 sm:px-10 md:px-12 py-2.5 sm:py-3 border-white text-white font-normal text-sm sm:text-base md:text-lg lg:text-xl hover:bg-white/10 transition-colors rounded-3xl w-auto h-10 sm:h-11 md:h-12"
            >
              Read more
            </Button>
          </div>

          {/* Navigation Arrows - RESPONSIVE */}
          <div className="flex justify-center md:justify-end gap-6 sm:gap-8 md:gap-10 mt-6 sm:mt-8 md:mt-10 md:pr-8 lg:pr-16 xl:pr-32">
            <Button
              variant="outlined"
              onClick={() =>
                setCurrentSlide(
                  (prev) => (prev - 1 + slides.length) % slides.length
                )
              }
              className="w-12 h-12 sm:w-14 sm:h-14 md:w-16 md:h-16 lg:w-[68px] lg:h-[56px] flex items-center justify-center text-white border-white rounded-full hover:bg-white/10 transition-colors"
            >
              <svg
                width="14"
                height="24"
                viewBox="0 0 15 26"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                className="w-3 h-5 sm:w-3.5 sm:h-6"
              >
                <path
                  d="M12.9961 0.589306L0.585449 13L12.9961 25.4106L14.4148 23.992L3.42145 13L14.4135 2.00797L12.9961 0.589306Z"
                  fill="currentColor"
                />
              </svg>
            </Button>
            <Button
              variant="outlined"
              onClick={() =>
                setCurrentSlide((prev) => (prev + 1) % slides.length)
              }
              className="w-12 h-12 sm:w-14 sm:h-14 md:w-16 md:h-16 lg:w-[68px] lg:h-[56px] flex items-center justify-center text-white border-white rounded-full hover:bg-white/10 transition-colors"
            >
              <svg
                width="14"
                height="24"
                viewBox="0 0 15 26"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                className="w-3 h-5 sm:w-3.5 sm:h-6"
              >
                <path
                  d="M2.00388 0.589306L14.4146 13L2.00388 25.4106L0.585217 23.992L11.5786 13L0.58655 2.00797L2.00388 0.589306Z"
                  fill="currentColor"
                />
              </svg>
            </Button>
          </div>
        </div>
      </Section>

      {/* ── Open Vacancies Section ── */}
      <div
        ref={jobsRef}
        className="py-12 sm:py-16 w-full overflow-hidden"
        style={{ background: "linear-gradient(180deg, #f8faff 0%, #ffffff 100%)" }}
      >
        {/* Section Header */}
        <div className="text-center mb-8 sm:mb-10 px-4">
          <h3 className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900 mb-2">
            Open Vacancies
          </h3>
          {!vacanciesLoading && (
            <p className="text-sm sm:text-base text-gray-500">
              {jobs === FALLBACK_JOBS
                ? "Sample positions — check back soon for live listings"
                : `${jobs.length} position${jobs.length !== 1 ? "s" : ""} currently available`}
            </p>
          )}
        </div>

        {/* Ticker or skeletons */}
        {vacanciesLoading ? (
          <div className="flex gap-4 sm:gap-5 overflow-x-hidden pb-4 px-6">
            {[1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="flex-shrink-0 w-[260px] sm:w-[300px] h-[180px] rounded-2xl bg-gray-100 animate-pulse"
              />
            ))}
          </div>
        ) : (
          <InfiniteTicker
            items={jobs}
            speed={0.6}
            renderItem={(item, idx) => {
              const hasSalary = item.salaryMin && item.salaryMax;
              const formattedSalaryMin = hasSalary
                ? parseFloat(item.salaryMin).toLocaleString(undefined, { maximumFractionDigits: 0 })
                : '';
              const formattedSalaryMax = hasSalary
                ? parseFloat(item.salaryMax).toLocaleString(undefined, { maximumFractionDigits: 0 })
                : '';

              return (
                <div
                  key={idx}
                  className="flex-shrink-0 w-[270px] sm:w-[310px] rounded-2xl border border-gray-100 bg-white shadow-md hover:shadow-xl transition-all duration-300 hover:-translate-y-1 overflow-hidden group cursor-default"
                >
                  {/* Top accent bar */}
                  {/* <div className="h-1.5 w-full" style={{ background: "linear-gradient(90deg, #0065AF, #0096D6)" }} /> */}

                  <div className="p-5 flex flex-col gap-3 h-[210px] justify-between">
                    <div className="flex flex-col gap-3.5">
                      {/* Title + Open badge */}
                      <div className="flex items-start justify-between gap-2">
                        <h4 className="font-normal text-gray-900 text-xs sm:text-sm leading-tight line-clamp-2 flex-1">
                          {item.title}
                        </h4>
                      </div>

                      {/* Detail row (Salary & Duration) */}
                      <div className="flex items-center justify-between gap-2">
                        {hasSalary ? (
                          <span className="text-[11px] font-medium text-emerald-700 bg-emerald-50/50 px-2 py-0.5 rounded border border-emerald-100/50">
                            💰 {formattedSalaryMin}-{formattedSalaryMax} {item.currency}
                          </span>
                        ) : (
                          <span className="text-[11px] font-medium text-gray-400">Salary TBD</span>
                        )}
                        {item.duration && (
                          <span className="text-[11px] font-medium text-blue-700 bg-blue-50/50 px-2 py-0.5 rounded border border-blue-100/50">
                            📅 {item.duration} Mos
                          </span>
                        )}
                      </div>

                      {/* Description / Remarks */}
                      <p className="text-xs text-gray-500 leading-relaxed line-clamp-2 italic">
                        {item.remarks || item.text || "Excellent opportunity. Click apply to submit your crew CV."}
                      </p>
                    </div>

                    {/* Footer Row */}
                    <div className="flex items-center justify-between pt-2.5 border-t border-gray-100">
                      <div className="flex items-center gap-1.5">
                        <div
                          className="w-5.5 h-5.5 rounded-full flex items-center justify-center flex-shrink-0"
                          style={{ background: "linear-gradient(135deg, #0065AF22, #0096D622)" }}
                        >
                          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#0065AF" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                            <circle cx="12" cy="5" r="3" /><line x1="12" y1="22" x2="12" y2="8" /><path d="M5 12H2a10 10 0 0 0 20 0h-3" />
                          </svg>
                        </div>
                        <span className="text-[10px] text-gray-400">Sakr Manning</span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            }}
          />
        )}
      </div>

      {/* CTA Section - RESPONSIVE */}
      <Section
        layout="centered"
        background="none"
        padding="md"
        className="w-full flex justify-center items-center px-4 sm:px-6"
      >
        <div className="w-full max-w-6xl 2xl:max-w-7xl min-h-[200px] sm:min-h-[220px] md:min-h-[235px] 2xl:min-h-[280px] bg-gradient-to-r from-blue-100 to-blue-200 rounded-xl flex flex-col items-center justify-center gap-6 sm:gap-8 py-8 sm:py-10 px-4 sm:px-6">
          {/* CTA Title */}
          <h2 className="font-semibold text-lg sm:text-xl md:text-2xl lg:text-3xl 2xl:text-4xl text-[#0065AF] text-center">
            APPLY FOR A JOB TODAY
          </h2>

          {/* CTA Buttons - RESPONSIVE */}
          <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 w-full sm:w-auto">
            <Button
              onClick={() => navigate("/quick-apply")}
              variant="primary"
              className="px-8 sm:px-10 md:px-12 py-3 sm:py-4 md:py-6 w-full sm:w-auto h-10 sm:h-11 md:h-12 font-medium rounded-3xl transition-colors text-sm sm:text-base"
            >
              Apply Form
            </Button>

            <Button
              variant="outlined"
              className="px-8 sm:px-10 md:px-12 py-3 sm:py-4 md:py-6 w-full sm:w-auto h-10 sm:h-11 md:h-12 text-[#0065AF] font-medium rounded-3xl transition-colors text-sm sm:text-base"
            >
              Upload CV
            </Button>
          </div>
        </div>
      </Section>
    </div>
  );
};

export default HomePage;
