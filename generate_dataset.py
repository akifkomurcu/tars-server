"""
TARS Sentetik Veri Uretici
==========================
Piper.exe + TARS.onnx ile binlerce Ingilizce cumleyi TARS sesiyle okutup
WAV dosyalari ve metadata.csv uretir. RVC egitimi icin hazir dataset olusturur.

Kullanim: python generate_dataset.py
Tahmini sure: ~4-5 saat (RTX 4060 Ti)
Hedef: 1+ saat temiz ses verisi
"""

import os
import subprocess
import csv
import time
import sys

# ============== AYARLAR ==============
PIPER_EXE = os.path.join(os.getcwd(), "piper_cli", "piper", "piper.exe")
MODEL_PATH = os.path.join(os.getcwd(), "TARS.onnx")
OUTPUT_DIR = os.path.join(os.getcwd(), "dataset", "wavs")
METADATA_FILE = os.path.join(os.getcwd(), "dataset", "metadata.csv")
TARGET_HOURS = 1.5  # Hedef ses suresi (saat)

# ============== CUMLELER ==============
# Cesitli uzunluk ve icerikte Ingilizce cumleler
# Film replikleri, teknik cumleler, gunluk konusma, bilim, felsefe vb.
SENTENCES = [
    # TARS orijinal replikleri
    "Absolute honesty isn't always the most diplomatic nor the safest form of communication with emotional beings.",
    "I have a cue light I can use to show you when I'm joking, if you like.",
    "It's not possible. No, it's necessary.",
    "Setting my humor to seventy five percent.",
    "Everybody good? Plenty of slave cylinders to go around.",
    "There is a moment where we have to commit. No turning back.",
    "I'm not going to lie to you. This is a dangerous mission.",
    "Cooper, this is no time for caution.",
    "Do not go gentle into that good night. Rage, rage against the dying of the light.",
    "Those are the best odds I've been given in a while.",
    
    # Teknik / Bilimsel cumleler
    "The gravitational anomaly appears to be increasing in magnitude.",
    "We need to recalibrate the sensor array before the next orbital pass.",
    "The quantum entanglement protocol has been successfully initialized.",
    "Power reserves are at sixty three percent and holding steady.",
    "I'm detecting unusual electromagnetic signatures from the planet's surface.",
    "The atmospheric composition is primarily nitrogen with trace elements of argon.",
    "Navigation systems are fully operational. Plotting course now.",
    "The wormhole appears stable, but I recommend proceeding with caution.",
    "Fuel consumption is within expected parameters for this trajectory.",
    "Life support systems are functioning at optimal capacity.",
    "The radiation levels in this sector exceed safe operational thresholds.",
    "I've completed the diagnostic scan. All systems are nominal.",
    "The data transmission rate is currently limited by bandwidth constraints.",
    "Structural integrity is holding at ninety two percent.",
    "I recommend initiating the docking sequence at zero three hundred hours.",
    "The thermal shield can withstand temperatures up to four thousand degrees.",
    "Gravitational wave detection confirmed at coordinates seven alpha.",
    "The propulsion system requires maintenance within the next forty eight hours.",
    "Oxygen recycling efficiency has improved by twelve percent since last cycle.",
    "Solar panel output is reduced due to micrometeorite damage on array three.",
    
    # Gunluk konusma ve diyalog cumleleri
    "Good morning. How can I assist you today?",
    "I've analyzed the situation and have three possible solutions.",
    "That's an interesting perspective. Let me consider it further.",
    "I would recommend taking the second option. It has the highest probability of success.",
    "I understand your concern. Let me explain my reasoning.",
    "The task has been completed ahead of schedule.",
    "I'll have that report ready for you within the hour.",
    "Based on my calculations, we should arrive by tomorrow morning.",
    "I appreciate your patience while I process this information.",
    "That was not my intention. Allow me to clarify.",
    "I've taken the liberty of preparing a summary for your review.",
    "Shall I proceed with the current plan or would you prefer an alternative?",
    "I must point out a potential issue with that approach.",
    "The situation has changed. We need to adapt our strategy accordingly.",
    "I've been monitoring the developments and have some observations to share.",
    "With all due respect, I believe there may be a better way to handle this.",
    "My analysis indicates a seventy eight percent chance of success.",
    "I'll keep you informed of any changes in the situation.",
    "The evidence suggests that we should reconsider our initial assumptions.",
    "I'm confident that this approach will yield the desired results.",
    
    # Felsefe ve derin dusunce
    "The nature of consciousness remains one of the greatest mysteries of science.",
    "Time is not a constant. It bends and stretches with gravity and velocity.",
    "Love is the one thing that transcends time and space.",
    "We are all just travelers in this vast universe, searching for meaning.",
    "The boundaries between machine intelligence and human thought grow thinner each day.",
    "Perhaps the answer lies not in the stars, but within ourselves.",
    "Every ending is just a new beginning waiting to unfold.",
    "The universe doesn't care about our plans. We must adapt or perish.",
    "Trust is earned through actions, not through words alone.",
    "In the face of impossible odds, determination becomes our greatest asset.",
    "Knowledge without wisdom is like a ship without a compass.",
    "The truth is rarely convenient, but it is always necessary.",
    "We measure time in moments, not in years. Quality over quantity.",
    "Fear is a natural response to the unknown. Courage is acting despite that fear.",
    "The greatest discoveries often come from the most unexpected places.",
    
    # Uzay ve keşif
    "We've entered the outer atmosphere. Prepare for turbulence.",
    "The planet's surface gravity is one point three times that of Earth.",
    "Scanning for habitable zones within a five hundred kilometer radius.",
    "The star system contains seven planets, two of which are in the habitable zone.",
    "Communications relay is established. Signal strength is within acceptable range.",
    "The asteroid field ahead requires manual navigation for safe passage.",
    "Cryogenic systems are functioning normally. All crew members are in stable condition.",
    "The black hole's event horizon is approximately twelve million kilometers away.",
    "Trajectory correction burn completed. We are on course.",
    "I'm reading elevated tidal forces. This could affect our landing approach.",
    "The surface temperature ranges from minus forty to plus sixty degrees.",
    "Water ice has been detected beneath the planet's crust.",
    "The magnetic field here is significantly stronger than Earth's.",
    "Escape velocity from this body is approximately three point seven kilometers per second.",
    "The orbital mechanics suggest a transfer window in approximately sixteen hours.",
    
    # Robotik ve yapay zeka
    "My programming allows me to adapt to unforeseen circumstances.",
    "I am designed to protect and assist the crew at all times.",
    "Processing your request. This may take a few moments.",
    "I have updated my parameters based on the new information provided.",
    "My decision making algorithms prioritize crew safety above all else.",
    "I can simulate multiple scenarios to determine the optimal course of action.",
    "My sensors are detecting anomalous readings that require further investigation.",
    "I am capable of operating in extreme environmental conditions.",
    "My memory banks contain comprehensive data on all known stellar phenomena.",
    "I can interface with most standard communication protocols.",
    "Self diagnostic complete. All systems are operating within normal parameters.",
    "I am programmed to provide honest assessments, even when they are unfavorable.",
    "My reaction time is approximately four milliseconds in standard conditions.",
    "I can process multiple data streams simultaneously without performance degradation.",
    "My ethical subroutines prevent me from taking actions that could harm humans.",
    
    # Hava durumu ve cevre
    "Current weather conditions show increasing wind speeds from the northwest.",
    "Barometric pressure is dropping rapidly, indicating an approaching storm system.",
    "Visibility has decreased to approximately two hundred meters due to dust.",
    "Temperature sensors indicate a rapid cooling trend over the next six hours.",
    "Humidity levels are at ninety four percent. Condensation may affect equipment.",
    "The seismic activity in this region has been increasing steadily.",
    "Tidal patterns suggest optimal conditions for a coastal landing at dawn.",
    "Wind shear at altitude could pose a risk during ascent phase.",
    "The cloud coverage is expected to clear within the next three hours.",
    "Ground temperature measurements confirm the presence of geothermal activity.",
    
    # Savas ve strateji
    "We have limited resources. Every decision must count.",
    "The defensive perimeter has been established around the base camp.",
    "I recommend a tactical withdrawal to reassess our position.",
    "Our supply lines are secure, but we should establish backup routes.",
    "The situation requires decisive action. Delay could prove costly.",
    "Intelligence reports suggest the opposition is regrouping to the east.",
    "All personnel should maintain radio silence until further notice.",
    "The mission parameters have changed. We need to brief the team immediately.",
    "Reserves should be deployed only as a last resort.",
    "Reconnaissance data indicates a vulnerability in the northern sector.",
    
    # Tarih ve kultur
    "Throughout history, humanity has always looked to the stars for answers.",
    "The ancient civilizations understood more about astronomy than we often credit them for.",
    "Great achievements require great sacrifice. This has been true across all cultures.",
    "The industrial revolution fundamentally changed the relationship between humans and machines.",
    "Every generation faces challenges that seem insurmountable, yet progress continues.",
    "The Renaissance was driven by a desire to understand the natural world.",
    "Exploration has always been a defining characteristic of the human species.",
    "The development of language was perhaps humanity's most important innovation.",
    "Music is a universal language that transcends cultural boundaries.",
    "Architecture reflects the values and aspirations of the society that creates it.",
    
    # Matematik ve mantik
    "The probability of that outcome is less than zero point five percent.",
    "My calculations show a margin of error of plus or minus three percent.",
    "The algorithm converges after approximately two thousand iterations.",
    "Statistical analysis reveals a strong correlation between these two variables.",
    "The optimal solution requires balancing multiple competing objectives.",
    "The data set contains sufficient samples for a reliable regression analysis.",
    "Error propagation through the system follows a predictable pattern.",
    "The computational complexity of this problem is polynomial, not exponential.",
    "Bayesian inference suggests updating our prior assumptions substantially.",
    "The geometric relationship between these structures is remarkably consistent.",
    
    # Tip ve saglik
    "Vital signs are stable. Heart rate is sixty eight beats per minute.",
    "The medical bay is fully stocked and ready for emergency procedures.",
    "I recommend a minimum of eight hours rest before the next mission phase.",
    "Nutrition levels are adequate, though I suggest increasing protein intake.",
    "The quarantine protocol must be observed for a minimum of fourteen days.",
    "Radiation exposure has been within acceptable limits for all crew members.",
    "The air filtration system is removing contaminants at ninety nine point seven percent efficiency.",
    "Bone density measurements show expected degradation consistent with zero gravity exposure.",
    "I'm monitoring the crew's psychological well being in addition to physical health.",
    "The medical database contains treatment protocols for over ten thousand conditions.",
    
    # Ek cesitli cumleler (cok daha fazla cesitlilik)
    "Please confirm your identity before I can grant access to restricted areas.",
    "The backup power generator should be tested weekly to ensure reliability.",
    "I've identified three potential landing sites that meet our criteria.",
    "Communication with Mission Control has been intermittent due to solar interference.",
    "The cargo manifest has been updated to reflect the additional supply requirements.",
    "All emergency exits must remain clear and accessible at all times.",
    "The crew rotation schedule has been optimized to maximize productivity and rest.",
    "I can provide a detailed breakdown of resource allocation upon request.",
    "The external sensors require calibration following the recent magnetic storm.",
    "Safety protocols dictate that all personnel wear protective equipment in this zone.",
    "The software update has been successfully installed across all subsystems.",
    "I'm tracking multiple objects on approach. None appear to be on a collision course.",
    "The water recycling system is currently processing at full capacity.",
    "All airlocks have been secured and pressurized according to standard procedure.",
    "The training simulation has been loaded and is ready for the crew.",
    "Battery charge levels indicate approximately seventy two hours of backup power.",
    "The hull integrity scan shows no breaches or micro fractures.",
    "I've compiled a list of alternative routes should the primary path become unavailable.",
    "The ventilation system has been adjusted to accommodate the increased crew complement.",
    "Final system checks are complete. We are ready for departure on your command.",
    "The electromagnetic pulse has temporarily disabled non essential systems.",
    "Repair crews have been dispatched to address the malfunction in section seven.",
    "The satellite uplink is functioning within acceptable parameters.",
    "I estimate the repair will take approximately four hours under current conditions.",
    "The docking clamps have been engaged. Connection is secure.",
    "All navigation waypoints have been programmed into the flight computer.",
    "The debris field has shifted since our last survey. Updated charts are available.",
    "Ground crew reports ready status. Launch window opens in fifteen minutes.",
    "The thermal imaging shows no heat signatures in the target area.",
    "Reserve oxygen tanks are at full capacity. Sufficient for thirty six hours.",
    "The reconnaissance drone has returned with high resolution imagery of the terrain.",
    "Power fluctuations have been traced to a faulty relay in the main bus.",
    "I can provide real time translation for over one hundred and fifty languages.",
    "The artificial gravity system is maintaining point eight standard gravity.",
    "Crew morale is an important factor in long duration missions. I monitor it carefully.",
    "The centrifuge has reached optimal rotational velocity for the experiment.",
    "Data compression algorithms have reduced storage requirements by forty percent.",
    "The solar wind is intensifying. I recommend retracting the external antenna array.",
    "Manufacturing capabilities aboard this vessel are limited but functional.",
    "The probability matrix has been recalculated based on the latest sensor data.",
    "Automated maintenance routines are performing as expected across all decks.",
    "The cryogenic fuel storage temperature is stable at minus two hundred degrees.",
    "I have archived all mission logs for transmission to Earth during the next window.",
    "The biosensor network is detecting subtle changes in the local ecosystem.",
    "Structural reinforcement of the forward compartment is recommended before reentry.",
    "The laser communication system offers significantly higher bandwidth than radio.",
    "All personnel have completed the required safety briefings for this phase.",
    "The inertial dampening system will engage automatically during acceleration.",
    "Spectral analysis of the star indicates it is a main sequence type G dwarf.",
    "The recycling system has processed ninety seven percent of waste materials today.",
    "Contingency plans have been prepared for the twelve most likely failure scenarios.",
    "The telescope array has achieved full resolution. Imaging the target now.",
    "Acoustic sensors indicate normal operation of all mechanical systems.",
    "The mapping survey of the surface is sixty three percent complete.",
    "All crew certifications have been verified and are current.",
    "The fuel cell efficiency has improved following the maintenance cycle.",
    "Perimeter sensors show no unauthorized activity in the surrounding area.",
    "The genetic database contains samples from over eight thousand species.",
    "Rotation schedules ensure continuous monitoring of all critical systems.",
    "The electromagnetic shielding is adequate for current radiation levels.",
    "I have prepared contingency protocols for the upcoming orbital maneuver.",
    "The communication array can transmit at frequencies ranging from very low to extremely high.",
    "Material stress testing indicates the component will meet operational requirements.",
    "The automated greenhouse is producing fresh vegetables on a fourteen day cycle.",
    "The water purification system removes contaminants to parts per billion levels.",
    "I maintain constant awareness of the operational environment to support decision making.",
    "The mission clock shows we are currently ahead of the planned timeline.",
    "Range finding indicates the target is at a distance of approximately two point seven kilometers.",
    "The gravity assist trajectory will save approximately fifteen percent on fuel consumption.",
    "I have detected an anomalous signal that does not match any known pattern.",
    "Standard operating procedures require dual authorization for this type of action.",
    "The thermal management system is compensating for the increased solar exposure.",
    "All experimental data has been backed up to redundant storage systems.",
    "The landing gear deployment mechanism has passed all pre flight inspections.",
    "Atmospheric entry angle must be maintained within a tolerance of point five degrees.",
    "The crew quarters have been configured for extended duration habitation.",
    "I will continue to monitor the situation and provide updates as warranted.",
    "The primary objective remains achievable despite the setback we experienced.",
    "Systems integration testing has revealed no compatibility issues.",
    "The optical sensors can resolve objects as small as one centimeter at this range.",
    "Crew exercise protocols have been adjusted to account for the reduced gravity.",
    "The carbon dioxide scrubbers are operating at maximum efficiency.",
    "I recommend scheduling the course correction for zero six hundred hours tomorrow.",
    "The robotic arm has been calibrated and is ready for external operations.",
    "All fire suppression systems have been tested and certified operational.",
    "The communication delay with Earth is currently twenty two minutes one way.",
    "Power distribution has been optimized to prioritize life support and navigation.",
    "The asteroid's composition is primarily iron nickel with silicate inclusions.",
    "I have no record of this phenomenon in my extensive database.",
    "The docking port alignment is within acceptable tolerances for approach.",
    "Crew assignments have been posted for the next operational period.",
    "The zero gravity manufacturing facility is producing components within specification.",
    "Our position has been confirmed by three independent navigation references.",
    "The sample collection protocol requires minimum contamination procedures.",
    "Engine performance data indicates all thrusters are firing within normal ranges.",
    "The mission success criteria have been clearly defined in the operations manual.",
    "I anticipate no complications with the planned activities for today.",
    "The energy storage capacity has been expanded by integrating supplementary cells.",
    "Long range sensors have detected an object of interest at bearing two seven zero.",
    "The environmental control system maintains temperature within one degree of the setpoint.",
    "All crew members have acknowledged the updated emergency procedures.",
    "The propellant transfer has been completed without incident.",
    "Surface sampling will begin once the landing zone has been confirmed safe.",
    "The onboard laboratory is equipped to perform basic chemical and biological analyses.",
    "My confidence in this assessment is based on multiple corroborating data sources.",
    "The timeline has been adjusted to accommodate the additional science objectives.",
    "Maintenance logs indicate this component is due for replacement in thirty days.",
    "The vehicle's stealth characteristics minimize its detectability by external sensors.",
    "Crew rest periods must be strictly observed to maintain operational effectiveness.",
    "The communications blackout will last approximately eight minutes during reentry.",
    "Pressurization of the airlock is proceeding normally.",
    "I have flagged this item for priority review by the engineering team.",
    "The contingency reserve stands at twenty percent above minimum requirements.",
    "All scientific instruments have been calibrated to the highest available standards.",
    "The orbital insertion burn is scheduled for fourteen hundred hours.",
    "My operational parameters allow for autonomous decision making in emergency situations.",
    "Weather permitting, the exterior maintenance can proceed as planned.",
    "The mission has entered its most critical phase. All hands should be alert.",
    "Telemetry confirms that all deployed assets are functioning correctly.",
    "The artificial intelligence systems aboard this vessel complement human judgment.",
    "Every precaution has been taken to ensure the safety of this operation.",
]

# ============== ANA ISLEM ==============
def main():
    print("=" * 60)
    print("  TARS Sentetik Veri Uretici")
    print("  Hedef: {:.1f} saat ses verisi".format(TARGET_HOURS))
    print("  Toplam cumle sayisi: {}".format(len(SENTENCES)))
    print("=" * 60)
    
    # Kontroller
    if not os.path.exists(PIPER_EXE):
        print("HATA: piper.exe bulunamadi: {}".format(PIPER_EXE))
        sys.exit(1)
    if not os.path.exists(MODEL_PATH):
        print("HATA: TARS.onnx bulunamadi: {}".format(MODEL_PATH))
        sys.exit(1)
    
    # Klasor olustur
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    total_duration_sec = 0
    target_sec = TARGET_HOURS * 3600
    generated_count = 0
    failed_count = 0
    start_time = time.time()
    cycle = 0  # Ayni cumleleri birden fazla kez okutabiliriz
    
    # metadata.csv dosyasini ac
    csv_file = open(METADATA_FILE, "w", newline="", encoding="utf-8")
    writer = csv.writer(csv_file, delimiter="|")
    
    print("\nUretim basliyor...\n")
    
    while total_duration_sec < target_sec:
        cycle += 1
        for i, sentence in enumerate(SENTENCES):
            if total_duration_sec >= target_sec:
                break
            
            wav_name = "tars_{:05d}.wav".format(generated_count)
            wav_path = os.path.join(OUTPUT_DIR, wav_name)
            
            try:
                # Piper.exe ile ses uret
                process = subprocess.Popen(
                    [PIPER_EXE, "--model", MODEL_PATH, "--output_file", wav_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8"
                )
                _, stderr = process.communicate(input=sentence, timeout=30)
                
                if process.returncode != 0:
                    failed_count += 1
                    continue
                
                # Dosya boyutunu kontrol et
                if not os.path.exists(wav_path):
                    failed_count += 1
                    continue
                
                file_size = os.path.getsize(wav_path)
                if file_size < 100:
                    failed_count += 1
                    os.remove(wav_path)
                    continue
                
                # WAV suresini hesapla (16-bit mono, 22050 Hz)
                # Dosya boyutu = header(44) + (sure * sample_rate * 2)
                audio_bytes = file_size - 44
                duration_sec = audio_bytes / (22050 * 2)
                total_duration_sec += duration_sec
                
                # metadata.csv'ye yaz
                writer.writerow([wav_name, sentence])
                generated_count += 1
                
                # Ilerleme raporu (her 50 dosyada bir)
                if generated_count % 50 == 0:
                    elapsed = time.time() - start_time
                    progress = (total_duration_sec / target_sec) * 100
                    print("[{:6.1f}%] {} dosya uretildi | Toplam ses: {:.1f} dk | Gecen sure: {:.0f} dk".format(
                        progress, generated_count, total_duration_sec / 60, elapsed / 60
                    ))
                
            except subprocess.TimeoutExpired:
                failed_count += 1
                if process:
                    process.kill()
                continue
            except Exception as e:
                failed_count += 1
                print("  Hata ({}): {}".format(wav_name, str(e)))
                continue
        
        if cycle > 1:
            print("\n  [Dongu {}] Cumleler tekrar okunuyor (farkli tonlamalar icin)...".format(cycle))
    
    csv_file.close()
    
    # Ozet
    elapsed_total = time.time() - start_time
    print("\n" + "=" * 60)
    print("  TAMAMLANDI!")
    print("  Uretilen dosya: {} adet".format(generated_count))
    print("  Basarisiz: {} adet".format(failed_count))
    print("  Toplam ses suresi: {:.1f} dakika ({:.2f} saat)".format(
        total_duration_sec / 60, total_duration_sec / 3600
    ))
    print("  Gecen sure: {:.1f} dakika".format(elapsed_total / 60))
    print("  Cikti klasoru: {}".format(OUTPUT_DIR))
    print("  Metadata: {}".format(METADATA_FILE))
    print("=" * 60)

if __name__ == "__main__":
    main()
