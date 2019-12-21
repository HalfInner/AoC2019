#include <iostream>
#include <algorithm>
#include <fstream>
#include <sstream>
#include <deque>
#include <string>
#include <numeric>

auto createInitialPhase(std::string input) {
    std::deque<int> phase;
    std::transform(begin(input), end(input), std::back_inserter(phase), [](auto &&c) { return c - '0'; });
    return phase;
}

auto parseFile(std::string path) {
    std::ifstream input(path);
    std::stringstream strStream;
    strStream << input.rdbuf();
    return strStream.str();
}

class PatternGenerator {
public:
    int next() const {
        const size_t offset = 1;
        size_t idx = (pos + offset) / seq % basePattern.size();
        ++pos;
        return basePattern.at(idx);
    }

    void incrementSequance() {
        pos = 0;
        ++seq;
    }

private:
    const std::deque<int> basePattern = {0, 1, 0, -1};
    mutable int pos = 0;
    int seq = 1;
};

auto calculateFft(std::deque<int> phase) {
    PatternGenerator pg;
    std::deque<int> next_phase;
    size_t pos = 0;
    for (size_t i = 0; i < phase.size(); ++i) {
        auto result = std::accumulate(begin(phase), end(phase), 0, [&pg](auto &&sum, auto &&in) {
            return sum + in * pg.next();
        });
        next_phase.push_back(std::abs(result) % 10);
        pg.incrementSequance();
    }

    return std::move(next_phase);
}

int main() {
    auto const inputFile = "day16_input.txt";
    auto phase = createInitialPhase(parseFile(inputFile));

    constexpr size_t seekPhase = 100;
    for (size_t phase_idx = 0; phase_idx < seekPhase; ++phase_idx) {
        phase = calculateFft(std::move(phase));
    }

    std::cout << "After " << seekPhase << " phases: \n";
    for (auto&& c : phase) {
        std::cout << c;
    }

    return 0;
}