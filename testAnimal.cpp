#include "Animal.h"
using namespace br::ufscar::lince::test;

#include <libcpputil/Functions.h>
using namespace cpputil;

#include <iostream>
using namespace std;

int main() {
	Animal animal1(Animal::GATO);
	Animal animal2 = Animal::PATO;
	Animal animal3(animal1);
	const Animal animal4 = animal2;
	Animal animal5("GALINHA");

	cout << "animal1: " << animal1 << endl;
	cout << "animal2: " << animal2 << endl;
	cout << "animal3: " << animal3 << endl;
	cout << "animal4: " << animal4 << endl;
	cout << "animal5: " << animal5 << endl << endl;

	cout << "animal1 == animal2: " << Functions::boolToString(animal1 == animal2) << endl;
	cout << "animal1 == animal3: " << Functions::boolToString(animal1 == animal3) << endl;
	cout << "animal1 == animal4: " << Functions::boolToString(animal1 == animal4) << endl;
	cout << "animal1 == animal5: " << Functions::boolToString(animal1 == animal5) << endl;
	cout << "animal2 == animal4: " << Functions::boolToString(animal2 == animal4) << endl << endl;


	cout << "animal1 != animal2: " << Functions::boolToString(animal1 != animal2) << endl;
	cout << "animal1 != animal3: " << Functions::boolToString(animal1 != animal3) << endl;
	cout << "animal1 != animal4: " << Functions::boolToString(animal1 != animal4) << endl;
	cout << "animal1 != animal5: " << Functions::boolToString(animal1 != animal5) << endl;
	cout << "animal2 != animal4: " << Functions::boolToString(animal2 != animal4) << endl << endl;

	cout << "animal1 == Animal::GATO: " << Functions::boolToString(animal1 == Animal::GATO) << endl;
	cout << "animal1 == Animal::PATO: " << Functions::boolToString(animal1 == Animal::PATO) << endl;
	cout << "animal1 != Animal::GATO: " << Functions::boolToString(animal1 != Animal::GATO) << endl;
	cout << "animal1 != Animal::PATO: " << Functions::boolToString(animal1 != Animal::PATO) << endl;
	return 0;
}
