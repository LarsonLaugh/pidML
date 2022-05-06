// pidtrain.cpp
#include<iostream>
#include<ctime> // for time()
#include<vector>
#include<chrono> // for chrono
#include<thread> // for this_thread
#include<numeric> // for accumulate()
#include<cmath> // for abs()
#include<random> // for random_device
#include<algorithm> // for sort()
#include<fstream> // for file I/O
#include<iostream>

#define ENVIRONMENT_TEMP 43
using namespace std;


struct pidcoef // PID coefficients
{
	float Kp;
	float Ki;
	float Kd;
	float cost = 0.0; // cost function value
};

class PID
{
private:
	pidcoef Kpid;
	float temp;
	float setpoint;
	float integral;
	float last_error;
	float start_time;
	float period;
	int curr_cycle;
public:
	PID(float kp, float ki, float kd, float sp, float pd) :
		temp(ENVIRONMENT_TEMP), Kpid({ kp, ki, kd }), setpoint(sp), period(pd), integral(0),
		last_error(0), start_time(std::time(0)), curr_cycle(1)
	{  }; // contructor
	//~PID(); // destructor
	float get_integral() const { return integral; }
	float get_last_error() const { return last_error; }
	float get_start_time() const { return start_time; }
	float get_setpoint() const { return setpoint; }
	float get_temp() const { return temp; }
	float get_curr_cycle() const { return curr_cycle; }
	float get_period() const { return period; }
	pidcoef get_pid() const { return Kpid; }
	void set_curr_cycle(int cc) { curr_cycle = cc; }
	void set_integral(float it) { integral = it; }
	void set_temp(float t) { temp = t; }
	void set_last_error(float le) { last_error = le; }

	float output() // calculate output for one PID cycle
	{
		float error = 0.0;
		float derivative = 0.0;
		error = setpoint - temp;
		integral = get_integral() + error;
		derivative = (error - get_last_error()) / get_period();
		set_integral(integral);
		set_last_error(error);

		return Kpid.Kp * error + Kpid.Ki * integral + Kpid.Kd * derivative;
	}
	float simulation(vector<float>* temp_logger, int cycle_num) // simulate for cycle_num PID cycles
	{
		set_curr_cycle(1);
		int n = 1;
		while (cycle_num + 1 > curr_cycle)
		{
			temp_logger->push_back(temp);
			if (output() > 0)
				set_temp(temp + 0.3);
			else
				set_temp(temp - 0.01);

			set_curr_cycle(++n);
		}
		vector<float> tempVtr;
		for (int i = 0; i < temp_logger->size(); i++)
			tempVtr.push_back(abs((*temp_logger)[i] - setpoint));
		float sum = accumulate(tempVtr.begin(), tempVtr.end(), 0);
		tempVtr.clear();
		return sum / temp_logger->size();
	};

};

void swap(float& a, float& b) // swap the values of a and b
{
	float temp;
	temp = a;
	a = b;
	b = temp;
}

void pid_hybrid(pidcoef& Kpid1, pidcoef& Kpid2) // hybrid two PID parameters and initialize
{
	int dice = (rand() % 3);
	switch (dice)
	{
	case 0:
	{
		swap(Kpid1.Ki, Kpid2.Ki);
		swap(Kpid1.Kd, Kpid2.Kd);
		Kpid1.cost = 0;
		Kpid2.cost = 0;
		break;
	}
	case 1:
	{
		swap(Kpid1.Kp, Kpid2.Kp);
		swap(Kpid1.Kd, Kpid2.Kd);
		Kpid1.cost = 0;
		Kpid2.cost = 0;
		break;
	}
	case 2:
	{
		swap(Kpid1.Ki, Kpid2.Ki);
		swap(Kpid1.Kp, Kpid2.Kp);
		Kpid1.cost = 0;
		Kpid2.cost = 0;
		break;
	}
	}

}


pidcoef pid_mutation() // generate random PID coefficients to realize mutation
{
	random_device rd; // obtain a random number from hardware
	mt19937 gen(rd()); // seed the generator
	uniform_int_distribution<> distr(0, 100); // define the range
	pidcoef Kpid;
	Kpid.Kp = distr(gen);
	Kpid.Ki = distr(gen);
	Kpid.Kd = distr(gen);
	Kpid.cost = 0;
	return Kpid;
}

void fill_random(vector<pidcoef>* vtr, int size) // fill a vector data with random float numbers
{
	random_device rd;
	mt19937 gen(rd());
	uniform_real_distribution<float> distr(0, 100);

	for (int i = 0; i < size; i++)
	{
		pidcoef new_kpid;
		new_kpid.Kp = distr(gen);
		new_kpid.Ki = distr(gen);
		new_kpid.Kd = distr(gen);
		vtr->push_back(new_kpid);
	};
};

bool cost_sorter(pidcoef const& Kpid1, pidcoef const& Kpid2) // sort by cost function value
{
	return Kpid1.cost < Kpid2.cost;
}


void genalg_simu(int GenMax, int PopSize, float setpoint, float period, int cycle_num) // For simulation
{
	vector<pidcoef> Kpid_vtr;
	fill_random(&Kpid_vtr, PopSize);
	for (int gen = 0; gen < GenMax; gen++)
	{
		cout << "\ngeneration # " << gen << endl;
		cout << "-------------\n" << endl;
		cout << "Kp, Ki, Kd, Cost \n" << endl;


		for (int i = 0; i < PopSize; i++)
		{
			PID pid(Kpid_vtr[i].Kp, Kpid_vtr[i].Ki, Kpid_vtr[i].Kd, setpoint, period);
			vector<float> temp_logger;
			Kpid_vtr[i].cost = pid.simulation(&temp_logger, cycle_num);


			cout << Kpid_vtr[i].Kp << ' ' << Kpid_vtr[i].Ki << ' ' << Kpid_vtr[i].Kd
				<< ' ' << Kpid_vtr[i].cost << '\n';
		};

		sort(Kpid_vtr.begin(), Kpid_vtr.end(), &cost_sorter);
		for (int j = 1; j < PopSize - 2; j += 2)
			pid_hybrid(Kpid_vtr[j], Kpid_vtr[j + 1]);
		if (PopSize % 2)
			Kpid_vtr[PopSize - 1] = pid_mutation();
		else
		{
			Kpid_vtr[PopSize - 2] = pid_mutation();
			Kpid_vtr[PopSize - 1] = pid_mutation();
		}
	};
};



int main()
{
	auto t1 = std::chrono::high_resolution_clock::now();
	float setpoint = 65;
	float period = 1;
	int GenMax = 100;
	int PopSize = 20;
	int cycle_num = 1000;
	genalg_simu(GenMax, PopSize, setpoint, period, cycle_num);
	auto t2 = std::chrono::high_resolution_clock::now();
	auto ms_int = std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1);
	std::cout << ms_int.count() << "ms\n"; // display runtime
	return 0;
}