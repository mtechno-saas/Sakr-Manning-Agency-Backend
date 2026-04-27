export function FormHeader({ steps, currentStep, goToStep, logo }) {
  return (
    <div className="w-full h-[361px] flex flex-col justify-between mx-auto py-6 bg-[#0065AF] shadow-lg rounded-[15px] relative z-10">
      {/* LOGO & TITLE */}
      <div className="flex flex-row justify-start mb-7 ml-3 gap-10">
        <img width="150px" height="150px" src={logo} />
        <div className="flex flex-col justify-center">
          <h1 className="text-white min-text-lg text-[52px]">
            {" "}
            SAKR MANNING AGENCY{" "}
          </h1>
          <p className="text-white/70 text-lg">
            {" "}
            FOR RECRUITING EGYPTIAN LABOR ABROAD{" "}
          </p>
        </div>
      </div>
      <div className="flex justify-center overflow-x-auto bg-white rounded-lg min-w-full -mx-[2px] py-3 shadow-lg">
        {/* Steps */}
        <div className="flex items-center backdrop-blur-sm min-w-max">
          {steps.map((step, i) => {
            return (
              <div key={i} className="flex items-center justify-between gap-16">
                <button
                  type="button"
                  onClick={() => goToStep(i)}
                  className={`flex flex-col m-0 items-center px-4 py-2 rounded-sm transition-all duration-300 
                      ${
                        currentStep === i
                          ? "text-[#0065AF] shadow-sm"
                          : currentStep > i
                          ? " text-black"
                          : " text-black hover:bg-white/30"
                      }`}
                >
                  <img width="40px" height="40px" src={step.icon[i]} />
                  <span className="text-xl font-small hidden sm:block">
                    {step.label}
                  </span>
                </button>
                {/* {i < steps.length - 1 && (
                  <div className="w-0 h-0.5 bg-black mx-0" />
                )} */}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
