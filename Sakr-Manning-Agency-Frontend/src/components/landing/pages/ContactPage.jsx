import React, { useState } from "react";
import Section from "../../common/Section";
import Card from "../../common/Card";
import Input from "../../common/Input";
import Button from "../../common/Button";
import ImageBlock from "../../common/ImageBlock";
import { MapPin, Phone, Mail, User } from "lucide-react";
import { ASSETS } from "../../../utils/constants";
import "../../../styles/globals.css";

const ContactPage = () => {
  const [form, setForm] = useState({
    name: "",
    email: "",
    subject: "",
    message: "",
  });

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = (e) => {
    e.preventDefault();
    alert("Message sent successfully!");
    setForm({ name: "", email: "", subject: "", message: "" });
  };

  const contactInfo = [
    {
      icon: MapPin,
      title: "Address",
      details: [
        "Building No. 136,",
        "5000 Units,",
        "Alzohor District,",
        "Port Said, Egypt.",
      ],
    },
    {
      icon: Phone,
      title: "Phone",
      details: [
        "Tel: +20 663699271",
        "Fax: +20 663699271",
        "Mob(EGY): +20 1009250111",
        "Mob(EGY): +20 1003245666",
      ],
    },
    {
      icon: Mail,
      title: "Email",
      details: [
        "info@sakrshipping.com",
        "sakrshipping@sakrshipping.com",
        "crew@sakrshipping.com",
      ],
      underline: true,
    },
  ];

  const teamMembers = [
    {
      name: "Mr. Osama Sakr",
      position: "Managing Director",
    },
    {
      name: "Mr. Amr Sakr",
      position: "Crew Manager",
    },
  ];

  return (
    <div className="w-full bg-white overflow-x-hidden">
      {/* Hero Section - RESPONSIVE */}
      <Section
        layout="centered"
        background="default"
        padding="md"
        margin="none"
        textAlign="center"
        className="px-4 sm:px-6"
      >
        <div className="space-y-3 sm:space-y-4 mt-4 sm:mt-6">
          <h1 className="font-semibold text-xl sm:text-2xl md:text-3xl lg:text-[32px] leading-tight text-black">
            Contact
          </h1>
          <p className="font-medium text-base sm:text-lg md:text-xl lg:text-[24px] 2xl:text-3xl leading-relaxed text-[#757575] max-w-2xl 2xl:max-w-4xl mx-auto px-4">
            Send us a message or call us for more information
          </p>
        </div>
      </Section>

      {/* Contact Info Cards - RESPONSIVE */}
      <Section
        layout="centered"
        background="default"
        padding="sm"
        className="container mx-auto max-w-7xl 2xl:max-w-[1400px] px-4 sm:px-6"
      >
        <div className="w-full grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8 md:gap-10 lg:gap-[82px]">
          {contactInfo.map((info, index) => {
            const IconComponent = info.icon;
            return (
              <Card
                key={index}
                variant="contact"
                className="relative flex flex-col justify-center items-center w-full min-h-[220px] sm:min-h-[240px] md:min-h-[246px] 2xl:min-h-[300px] bg-[rgba(36,119,195,0.1)] rounded-[22px] 2xl:rounded-[32px] p-4 sm:p-6 2xl:p-10"
              >
                {/* Icon */}
                <div className="absolute top-3 sm:top-4 left-1/2 transform -translate-x-1/2">
                  <IconComponent className="w-7 h-7 sm:w-8 sm:h-8 2xl:w-12 2xl:h-12 text-[#0065AF]" />
                </div>

                {/* Content */}
                <div className="flex flex-col justify-center items-center text-center gap-1 mt-8 sm:mt-10">
                  <div className="font-semibold text-lg sm:text-xl md:text-[24px] text-black">
                    {info.title}
                  </div>
                  <div
                    className={`font-normal text-sm sm:text-base md:text-lg lg:text-[20px] leading-snug text-black ${info.underline ? "underline" : ""
                      }`}
                  >
                    {info.details.map((detail, detailIndex) => (
                      <div key={detailIndex}>{detail}</div>
                    ))}
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      </Section>

      {/* Team Cards - RESPONSIVE */}
      <Section
        layout="centered"
        background="default"
        padding="sm"
        className="container mx-auto max-w-5xl 2xl:max-w-6xl px-4 sm:px-6"
      >
        <div className="w-full grid grid-cols-1 md:grid-cols-2 gap-6 sm:gap-8 md:gap-12 lg:gap-[183px]">
          {teamMembers.map((member, index) => (
            <Card
              key={index}
              variant="team"
              className="flex flex-row items-center justify-center gap-3 sm:gap-4 2xl:gap-6 w-full min-h-[140px] sm:min-h-[150px] md:min-h-[163px] 2xl:min-h-[200px] bg-white shadow-2xl rounded-[22px] 2xl:rounded-[32px] p-4 sm:p-6 2xl:p-10"
            >
              <User className="w-9 h-9 sm:w-10 sm:h-10 md:w-11 md:h-11 2xl:w-16 2xl:h-16 text-[#1E1E1E] flex-shrink-0" />
              <div className="text-center">
                <div className="font-medium text-base sm:text-lg md:text-xl lg:text-[28px] leading-tight text-black">
                  {member.name}
                </div>
                <div className="font-medium text-sm sm:text-base md:text-lg lg:text-[20px] text-black/80">
                  {member.position}
                </div>
              </div>
            </Card>
          ))}
        </div>
      </Section>

      {/* Map and Contact Form Section - RESPONSIVE */}
      <Section
        layout="split"
        background="default"
        padding="md"
        margin="none"
        className="container w-full max-w-7xl 2xl:max-w-[1400px] mx-auto flex flex-col lg:flex-row items-start justify-center gap-8 sm:gap-10 md:gap-12 lg:gap-[60px] px-4 sm:px-6 md:px-8"
      >
        {/* Map - RESPONSIVE */}
        <div className="w-full lg:w-1/2">
          <ImageBlock
            src={ASSETS.CONTACT}
            alt="Map showing our location"
            aspectRatio="auto"
            rounded="xl"
            className="w-full h-[300px] sm:h-[400px] md:h-[450px] lg:h-[520px] 2xl:h-[600px] object-cover"
            loading="lazy"
          />
        </div>

        {/* Contact Form - RESPONSIVE */}
        <div className="w-full lg:w-1/2 space-y-4 sm:space-y-6">
          <h2 className="font-semibold text-xl sm:text-2xl md:text-3xl lg:text-[32px] leading-tight text-black mb-4 sm:mb-6">
            Send a Message to Us
          </h2>

          <form onSubmit={handleSubmit} className="space-y-3 sm:space-y-4">
            {/* Name Input - RESPONSIVE */}
            <Input
              type="text"
              name="name"
              value={form.name}
              onChange={handleChange}
              placeholder="Enter your name"
              variant="contact"
              className="w-full h-14 sm:h-16 md:h-[70px] 2xl:h-[90px] border border-[#1976D2] rounded-[22px] 2xl:rounded-[30px] px-4 sm:px-6 py-4 sm:py-5 text-base sm:text-lg md:text-[20px] 2xl:text-2xl placeholder-black/50"
            />

            {/* Email Input - RESPONSIVE */}
            <Input
              type="email"
              name="email"
              value={form.email}
              onChange={handleChange}
              placeholder="Enter your email"
              variant="contact"
              className="w-full h-14 sm:h-16 md:h-[70px] 2xl:h-[90px] border border-[#1976D2] rounded-[22px] 2xl:rounded-[30px] px-4 sm:px-6 py-4 sm:py-5 text-base sm:text-lg md:text-[20px] 2xl:text-2xl placeholder-black/50"
            />

            {/* Subject Input - RESPONSIVE */}
            <Input
              type="text"
              name="subject"
              value={form.subject}
              onChange={handleChange}
              placeholder="Subject"
              variant="contact"
              className="w-full h-14 sm:h-16 md:h-[70px] 2xl:h-[90px] border border-[#1976D2] rounded-[22px] 2xl:rounded-[30px] px-4 sm:px-6 py-4 sm:py-5 text-base sm:text-lg md:text-[20px] 2xl:text-2xl placeholder-black/50"
            />

            {/* Message Textarea - RESPONSIVE */}
            <div className="relative">
              <textarea
                name="message"
                value={form.message}
                onChange={handleChange}
                placeholder="Message"
                className="w-full h-[150px] sm:h-[170px] md:h-[187px] 2xl:h-[250px] border border-[#1976D2] rounded-[22px] 2xl:rounded-[30px] px-4 sm:px-6 py-4 sm:py-5 text-base sm:text-lg md:text-[20px] 2xl:text-2xl placeholder-black/50 bg-transparent outline-none resize-none"
              />
            </div>
          </form>
        </div>
      </Section>

      {/* Send Button - RESPONSIVE */}
      <Section
        layout="centered"
        background="default"
        padding="none"
        className="container mx-auto max-w-4xl mb-12 sm:mb-14 md:mb-16 mt-4 sm:mt-6 px-4 sm:px-6"
      >
        <Button
          onClick={handleSubmit}
          variant="primary"
          size="lg"
          className="w-full max-w-[661px] 2xl:max-w-4xl h-12 sm:h-14 md:h-[60px] 2xl:h-20 bg-[#0065AF] hover:bg-[#2477C3] rounded-[24px] 2xl:rounded-[32px] transition-colors font-normal text-lg sm:text-xl md:text-[24px] 2xl:text-3xl text-white"
        >
          Send a message
        </Button>
      </Section>
    </div>
  );
};

export default ContactPage;
